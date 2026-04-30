"""Unit tests for archetypes_core.corroboration.

LLM-free: all adapters are stubs implemented inline.

Tests per §Tests "PR 1":
1. corroborate() returns clean when adapter scores clean
2. Returns flagged with correct citations when adapter scores flagged
3. Returns uncertain when adapter raises SubstrateUnavailable
4. Freshness budget passed through to adapter retrieve
5. CorroborationResult round-trips through JSON without information loss
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from archetypes_core.corroboration import (
    Citation,
    CorroborationResult,
    FreshnessBudget,
    PrimitiveDecomposition,
    Substrate,
    SubstrateAdapter,
    SubstrateUnavailable,
    corroborate,
)


# ---------------------------------------------------------------------------
# Stub adapters
# ---------------------------------------------------------------------------

FIXED_STAMP = datetime(2026, 4, 30, 12, 0, 0, tzinfo=timezone.utc)


class CleanAdapter:
    """Adapter that always returns a clean verdict."""

    scope_id = "stub-clean"
    captured_freshness: FreshnessBudget | None = None

    def retrieve(self, claim: str, freshness: FreshnessBudget) -> Substrate:
        CleanAdapter.captured_freshness = freshness
        return Substrate(scope_id=self.scope_id, retrieved_at=FIXED_STAMP, payload={"text": "all good"})

    def score(self, claim: str, substrate: Substrate) -> CorroborationResult:
        return CorroborationResult(
            verdict="clean",
            claim=claim,
            citations=[Citation(source_id="doc-1", excerpt="matches claim", provenance="grep")],
            freshness_stamp=FIXED_STAMP,
            scope_id=self.scope_id,
        )


class FlaggedAdapter:
    """Adapter that always returns flagged with one citation."""

    scope_id = "stub-flagged"

    def retrieve(self, claim: str, freshness: FreshnessBudget) -> Substrate:
        return Substrate(scope_id=self.scope_id, retrieved_at=FIXED_STAMP, payload={"text": "conflicting"})

    def score(self, claim: str, substrate: Substrate) -> CorroborationResult:
        return CorroborationResult(
            verdict="flagged",
            claim=claim,
            citations=[
                Citation(
                    source_id="world-primitive:death-as-renewal",
                    excerpt="Death here is transformation, not cessation.",
                    provenance="world_primitives table",
                )
            ],
            freshness_stamp=FIXED_STAMP,
            scope_id=self.scope_id,
            drift_class="tonal",
            notes="Claim implies permanent ending; world treats death as cycle.",
        )


class UnavailableAdapter:
    """Adapter whose retrieve always raises SubstrateUnavailable."""

    scope_id = "stub-unavailable"

    def retrieve(self, claim: str, freshness: FreshnessBudget) -> Substrate:
        raise SubstrateUnavailable(scope_id=self.scope_id, reason="DB offline")

    def score(self, claim: str, substrate: Substrate) -> CorroborationResult:  # pragma: no cover
        raise AssertionError("score() should not be called when retrieve raises")


class FreshnessCapturingAdapter:
    """Adapter that records the freshness budget passed to retrieve."""

    scope_id = "stub-freshness"
    _received: list[FreshnessBudget] = []

    def retrieve(self, claim: str, freshness: FreshnessBudget) -> Substrate:
        FreshnessCapturingAdapter._received.append(freshness)
        return Substrate(scope_id=self.scope_id, retrieved_at=FIXED_STAMP, payload=None)

    def score(self, claim: str, substrate: Substrate) -> CorroborationResult:
        return CorroborationResult(
            verdict="clean",
            claim=claim,
            citations=[],
            freshness_stamp=FIXED_STAMP,
            scope_id=self.scope_id,
        )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCorroborate:
    def test_clean_verdict(self):
        """corroborate() returns clean when adapter scores clean."""
        result = corroborate("The sky is bright", CleanAdapter(), FreshnessBudget.RECENT)
        assert result.verdict == "clean"
        assert result.claim == "The sky is bright"
        assert result.scope_id == "stub-clean"
        assert len(result.citations) == 1
        assert result.citations[0].source_id == "doc-1"

    def test_flagged_verdict_with_citations(self):
        """Returns flagged with correct citations when adapter scores flagged."""
        result = corroborate(
            "The dead are gone forever",
            FlaggedAdapter(),
            FreshnessBudget.HOUR,
        )
        assert result.verdict == "flagged"
        assert result.drift_class == "tonal"
        assert len(result.citations) == 1
        cit = result.citations[0]
        assert cit.source_id == "world-primitive:death-as-renewal"
        assert "transformation" in cit.excerpt
        assert result.notes is not None and "cycle" in result.notes

    def test_uncertain_when_substrate_unavailable(self):
        """Returns uncertain when adapter raises SubstrateUnavailable."""
        result = corroborate("Any claim", UnavailableAdapter(), FreshnessBudget.ANY)
        assert result.verdict == "uncertain"
        assert result.scope_id == "stub-unavailable"
        assert result.citations == []
        assert result.notes is not None and "DB offline" in result.notes

    def test_freshness_budget_passed_through(self):
        """Freshness budget is passed through unchanged to adapter.retrieve."""
        FreshnessCapturingAdapter._received.clear()
        for budget in (FreshnessBudget.REALTIME, FreshnessBudget.DAY, FreshnessBudget.ANY):
            corroborate("claim", FreshnessCapturingAdapter(), budget)
        assert FreshnessCapturingAdapter._received == [
            FreshnessBudget.REALTIME,
            FreshnessBudget.DAY,
            FreshnessBudget.ANY,
        ]

    def test_json_round_trip(self):
        """CorroborationResult round-trips through JSON without information loss."""
        decomp = PrimitiveDecomposition(
            primitives=["duty-over-desire", "rhythmic-process"],
            weights=[0.7, 0.3],
            decomposition_method="manual",
            decomposed_at="2026-04-30T12:00:00+00:00",
        )
        original = CorroborationResult(
            verdict="flagged",
            claim="The seasons obey the god's heartbeat",
            citations=[
                Citation(
                    source_id="world-primitive:seasons-as-breath",
                    excerpt="Seasons are the god's exhalation.",
                    provenance="world_primitives table",
                )
            ],
            freshness_stamp=FIXED_STAMP,
            scope_id="dead-god-world",
            drift_class="isomorphic",
            notes="Claim aligns with the seasons-as-breath isomorphic link.",
            primitive_decomposition=decomp,
        )

        serialised = original.to_json()
        restored = CorroborationResult.from_json(serialised)

        assert restored.verdict == original.verdict
        assert restored.claim == original.claim
        assert restored.scope_id == original.scope_id
        assert restored.drift_class == original.drift_class
        assert restored.notes == original.notes
        assert restored.freshness_stamp == original.freshness_stamp

        assert len(restored.citations) == 1
        c = restored.citations[0]
        assert c.source_id == "world-primitive:seasons-as-breath"
        assert c.excerpt == "Seasons are the god's exhalation."
        assert c.provenance == "world_primitives table"

        assert restored.primitive_decomposition is not None
        pd = restored.primitive_decomposition
        assert pd.primitives == ["duty-over-desire", "rhythmic-process"]
        assert pd.weights == [0.7, 0.3]
        assert pd.decomposition_method == "manual"
        assert pd.decomposed_at == "2026-04-30T12:00:00+00:00"

    def test_adapter_protocol_check(self):
        """SubstrateAdapter is a runtime-checkable Protocol."""
        # All three stubs satisfy the protocol at runtime
        for adapter in (CleanAdapter(), FlaggedAdapter(), UnavailableAdapter()):
            assert isinstance(adapter, SubstrateAdapter)
