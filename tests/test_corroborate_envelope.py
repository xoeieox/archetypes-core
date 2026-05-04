"""Tests for corroborate_envelope() and ProvenanceCapableAdapter (Move 3 Surface 1).

All 13 test cases from the spec:
1.  corroborate() unchanged — existing behavior unaffected.
2.  corroborate_envelope() returns LapisToolReturn.
3.  Payload identity — CorroborationResult plugs in unchanged.
4.  Summary populated — non-empty, contains verdict word.
5.  Envelope citations match payload citations.
6.  Envelope primitive_decomposition matches (present and absent).
7.  Envelope scope_id matches result.scope_id.
8.  Adapter without score_provenance → model/prompt_hash None, upstream_calls [].
9.  Adapter with score_provenance → fields populated.
10. Caller-supplied upstream_calls preserved when adapter also provides them.
11. SubstrateUnavailable path → returns LapisToolReturn, not raises.
12. manifest_hash deterministic — same inputs → same hash.
13. Round-trip — LapisToolReturn.from_dict(result.to_dict()) is equivalent.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from archetypes_core.corroboration import (
    Citation,
    CorroborationResult,
    FreshnessBudget,
    PrimitiveDecomposition,
    ProvenanceCapableAdapter,
    Substrate,
    SubstrateAdapter,
    SubstrateUnavailable,
    corroborate,
    corroborate_envelope,
)
from archetypes_core.provenance import LapisToolReturn, UpstreamRef

# Re-use fixtures from the existing test module.
from tests.test_corroboration import (
    FIXED_STAMP,
    CleanAdapter,
    FlaggedAdapter,
    UnavailableAdapter,
)

AGENT_ID = "test-agent/corroborate"
CLAIM = "The sky is bright"


# ---------------------------------------------------------------------------
# Additional stub adapters
# ---------------------------------------------------------------------------


class ProvenanceAdapter:
    """Adapter that implements score_provenance() and returns LLM metadata."""

    scope_id = "stub-provenance"

    def retrieve(self, claim: str, freshness: FreshnessBudget) -> Substrate:
        return Substrate(scope_id=self.scope_id, retrieved_at=FIXED_STAMP, payload={"text": "ok"})

    def score(self, claim: str, substrate: Substrate) -> CorroborationResult:
        return CorroborationResult(
            verdict="clean",
            claim=claim,
            citations=[Citation(source_id="doc-prov", excerpt="provenance doc", provenance_method="grep")],
            freshness_stamp=FIXED_STAMP,
            scope_id=self.scope_id,
        )

    def score_provenance(self) -> dict:
        return {
            "model": "test-model",
            "prompt_hash": "sha256:abc123",
            "upstream_calls": [
                UpstreamRef(agent_id="inner-agent", manifest_hash="sha256:def456"),
            ],
        }


class DecompositionAdapter:
    """Adapter that emits a PrimitiveDecomposition in its score result."""

    scope_id = "stub-decomp"

    def retrieve(self, claim: str, freshness: FreshnessBudget) -> Substrate:
        return Substrate(scope_id=self.scope_id, retrieved_at=FIXED_STAMP, payload={})

    def score(self, claim: str, substrate: Substrate) -> CorroborationResult:
        decomp = PrimitiveDecomposition(
            primitives=["duty-over-desire"],
            weights=[1.0],
            decomposition_method="manual",
            decomposed_at="2026-05-03T00:00:00+00:00",
        )
        return CorroborationResult(
            verdict="clean",
            claim=claim,
            citations=[],
            freshness_stamp=FIXED_STAMP,
            scope_id=self.scope_id,
            primitive_decomposition=decomp,
        )


# ---------------------------------------------------------------------------
# Test 1: corroborate() unchanged
# ---------------------------------------------------------------------------


class TestCorroborateUnchanged:
    def test_clean_verdict(self):
        result = corroborate(CLAIM, CleanAdapter(), FreshnessBudget.RECENT)
        assert result.verdict == "clean"
        assert isinstance(result, CorroborationResult)
        assert result.scope_id == "stub-clean"

    def test_flagged_verdict(self):
        result = corroborate("The dead are gone forever", FlaggedAdapter(), FreshnessBudget.HOUR)
        assert result.verdict == "flagged"
        assert result.drift_class == "tonal"

    def test_uncertain_verdict(self):
        result = corroborate(CLAIM, UnavailableAdapter(), FreshnessBudget.ANY)
        assert result.verdict == "uncertain"
        assert result.citations == []


# ---------------------------------------------------------------------------
# Test 2: corroborate_envelope() returns LapisToolReturn
# ---------------------------------------------------------------------------


class TestEnvelopeType:
    def test_returns_lapis_tool_return(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert isinstance(envelope, LapisToolReturn)


# ---------------------------------------------------------------------------
# Test 3: Payload identity
# ---------------------------------------------------------------------------


class TestPayloadIdentity:
    def test_payload_is_corroboration_result(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert isinstance(envelope.payload, CorroborationResult)

    def test_payload_verdict_and_claim(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert envelope.payload.verdict == "clean"
        assert envelope.payload.claim == CLAIM

    def test_payload_not_mutated(self):
        adapter = CleanAdapter()
        result = corroborate(CLAIM, adapter, FreshnessBudget.RECENT)
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        # CorroborationResult is not mutated: fields still match independent call
        assert envelope.payload.verdict == result.verdict
        assert envelope.payload.scope_id == result.scope_id


# ---------------------------------------------------------------------------
# Test 4: Summary populated
# ---------------------------------------------------------------------------


class TestSummaryPopulated:
    def test_clean_summary_non_empty(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert envelope.summary
        assert "clean" in envelope.summary

    def test_flagged_summary_contains_verdict(self):
        envelope = corroborate_envelope(
            "The dead are gone forever", FlaggedAdapter(), FreshnessBudget.HOUR, agent_id=AGENT_ID
        )
        assert envelope.summary
        assert "flagged" in envelope.summary

    def test_uncertain_summary_contains_verdict(self):
        envelope = corroborate_envelope(CLAIM, UnavailableAdapter(), FreshnessBudget.ANY, agent_id=AGENT_ID)
        assert envelope.summary
        assert "uncertain" in envelope.summary

    def test_flagged_summary_includes_drift_class(self):
        # FlaggedAdapter returns drift_class="tonal"
        envelope = corroborate_envelope(
            "The dead are gone forever", FlaggedAdapter(), FreshnessBudget.HOUR, agent_id=AGENT_ID
        )
        assert "tonal" in envelope.summary


# ---------------------------------------------------------------------------
# Test 5: Envelope citations match payload citations
# ---------------------------------------------------------------------------


class TestEnvelopeCitations:
    def test_citations_equal(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert envelope.provenance.citations == envelope.payload.citations

    def test_citations_content(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert len(envelope.provenance.citations) == 1
        assert envelope.provenance.citations[0].source_id == "doc-1"


# ---------------------------------------------------------------------------
# Test 6: Envelope primitive_decomposition matches
# ---------------------------------------------------------------------------


class TestEnvelopeDecomposition:
    def test_decomposition_lifted_when_present(self):
        envelope = corroborate_envelope(CLAIM, DecompositionAdapter(), FreshnessBudget.ANY, agent_id=AGENT_ID)
        assert envelope.provenance.primitive_decomposition is not None
        assert envelope.provenance.primitive_decomposition == envelope.payload.primitive_decomposition

    def test_decomposition_none_when_absent(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert envelope.provenance.primitive_decomposition is None
        assert envelope.payload.primitive_decomposition is None


# ---------------------------------------------------------------------------
# Test 7: Envelope scope_id matches result.scope_id
# ---------------------------------------------------------------------------


class TestEnvelopeScopeId:
    def test_scope_id_matches(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert envelope.provenance.scope_id == envelope.payload.scope_id

    def test_scope_id_value(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert envelope.provenance.scope_id == "stub-clean"


# ---------------------------------------------------------------------------
# Test 8: Adapter without score_provenance
# ---------------------------------------------------------------------------


class TestAdapterWithoutScoreProvenance:
    def test_model_none(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert envelope.provenance.model is None

    def test_prompt_hash_none(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert envelope.provenance.prompt_hash is None

    def test_upstream_calls_empty(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert envelope.provenance.upstream_calls == []

    def test_caller_supplied_upstream_preserved(self):
        caller_ref = UpstreamRef(agent_id="caller-agent", manifest_hash="sha256:caller123")
        envelope = corroborate_envelope(
            CLAIM, CleanAdapter(), FreshnessBudget.RECENT,
            agent_id=AGENT_ID,
            upstream_calls=[caller_ref],
        )
        assert len(envelope.provenance.upstream_calls) == 1
        assert envelope.provenance.upstream_calls[0].agent_id == "caller-agent"


# ---------------------------------------------------------------------------
# Test 9: Adapter with score_provenance
# ---------------------------------------------------------------------------


class TestAdapterWithScoreProvenance:
    def test_model_populated(self):
        envelope = corroborate_envelope(CLAIM, ProvenanceAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert envelope.provenance.model == "test-model"

    def test_prompt_hash_populated(self):
        envelope = corroborate_envelope(CLAIM, ProvenanceAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert envelope.provenance.prompt_hash == "sha256:abc123"

    def test_upstream_calls_populated(self):
        envelope = corroborate_envelope(CLAIM, ProvenanceAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        assert len(envelope.provenance.upstream_calls) == 1
        assert envelope.provenance.upstream_calls[0].agent_id == "inner-agent"


# ---------------------------------------------------------------------------
# Test 10: Caller-supplied upstream_calls preserved — caller first
# ---------------------------------------------------------------------------


class TestUpstreamCallsMerge:
    def test_caller_first_then_adapter(self):
        caller_ref = UpstreamRef(agent_id="caller-agent", manifest_hash="sha256:caller999")
        envelope = corroborate_envelope(
            CLAIM, ProvenanceAdapter(), FreshnessBudget.RECENT,
            agent_id=AGENT_ID,
            upstream_calls=[caller_ref],
        )
        calls = envelope.provenance.upstream_calls
        assert len(calls) == 2
        assert calls[0].agent_id == "caller-agent"   # caller first
        assert calls[1].agent_id == "inner-agent"    # adapter after

    def test_multiple_caller_refs_preserved(self):
        refs = [
            UpstreamRef(agent_id="caller-1", manifest_hash="sha256:aaa"),
            UpstreamRef(agent_id="caller-2", manifest_hash="sha256:bbb"),
        ]
        envelope = corroborate_envelope(
            CLAIM, ProvenanceAdapter(), FreshnessBudget.RECENT,
            agent_id=AGENT_ID,
            upstream_calls=refs,
        )
        calls = envelope.provenance.upstream_calls
        assert len(calls) == 3
        assert calls[0].agent_id == "caller-1"
        assert calls[1].agent_id == "caller-2"
        assert calls[2].agent_id == "inner-agent"


# ---------------------------------------------------------------------------
# Test 11: SubstrateUnavailable path → returns LapisToolReturn, not raises
# ---------------------------------------------------------------------------


class TestSubstrateUnavailablePath:
    def test_returns_envelope_not_raises(self):
        envelope = corroborate_envelope(CLAIM, UnavailableAdapter(), FreshnessBudget.ANY, agent_id=AGENT_ID)
        assert isinstance(envelope, LapisToolReturn)

    def test_payload_uncertain(self):
        envelope = corroborate_envelope(CLAIM, UnavailableAdapter(), FreshnessBudget.ANY, agent_id=AGENT_ID)
        assert envelope.payload.verdict == "uncertain"

    def test_summary_non_empty(self):
        envelope = corroborate_envelope(CLAIM, UnavailableAdapter(), FreshnessBudget.ANY, agent_id=AGENT_ID)
        assert envelope.summary
        assert "uncertain" in envelope.summary


# ---------------------------------------------------------------------------
# Test 12: manifest_hash deterministic
# ---------------------------------------------------------------------------


class TestManifestHashDeterministic:
    def test_same_inputs_same_hash(self):
        fixed_ts = datetime(2026, 5, 3, 12, 0, 0, tzinfo=timezone.utc)
        with patch("archetypes_core.provenance.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_ts
            mock_dt.fromisoformat = datetime.fromisoformat
            env1 = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
            env2 = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)

        assert env1.provenance.manifest_hash == env2.provenance.manifest_hash
        assert env1.provenance.manifest_hash.startswith("sha256:")

    def test_different_agents_different_hash(self):
        fixed_ts = datetime(2026, 5, 3, 12, 0, 0, tzinfo=timezone.utc)
        with patch("archetypes_core.provenance.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_ts
            mock_dt.fromisoformat = datetime.fromisoformat
            env1 = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id="agent-a")
            env2 = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id="agent-b")

        assert env1.provenance.manifest_hash != env2.provenance.manifest_hash


# ---------------------------------------------------------------------------
# Test 13: Round-trip
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_provenance_survives_round_trip(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        restored = LapisToolReturn.from_dict(envelope.to_dict())

        assert restored.provenance.schema_version == envelope.provenance.schema_version
        assert restored.provenance.manifest_hash == envelope.provenance.manifest_hash
        assert restored.provenance.agent_id == envelope.provenance.agent_id
        assert restored.provenance.tool == envelope.provenance.tool
        assert restored.provenance.scope_id == envelope.provenance.scope_id
        assert restored.summary == envelope.summary

    def test_payload_survives_round_trip_as_dict(self):
        # from_dict stores payload as plain dict (not CorroborationResult)
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        restored = LapisToolReturn.from_dict(envelope.to_dict())
        assert restored.payload == envelope.payload.to_dict()

    def test_citations_survive_round_trip(self):
        envelope = corroborate_envelope(CLAIM, CleanAdapter(), FreshnessBudget.RECENT, agent_id=AGENT_ID)
        restored = LapisToolReturn.from_dict(envelope.to_dict())
        assert len(restored.provenance.citations) == len(envelope.provenance.citations)
        assert restored.provenance.citations[0].source_id == envelope.provenance.citations[0].source_id


# ---------------------------------------------------------------------------
# ProvenanceCapableAdapter Protocol check
# ---------------------------------------------------------------------------


class TestProvenanceCapableAdapterProtocol:
    def test_provenance_adapter_is_instance(self):
        assert isinstance(ProvenanceAdapter(), ProvenanceCapableAdapter)

    def test_clean_adapter_is_not_instance(self):
        assert not isinstance(CleanAdapter(), ProvenanceCapableAdapter)
