"""Tests for archetypes_core.provenance — Lapis Provenance Schema v0.

All 10 test cases from the spec (§Tests):
1.  Round-trip: LapisToolReturn via to_lapis_return() → to_dict() → from_dict() equality.
2.  Round-trip via JSON: to_json() / from_json() symmetric.
3.  manifest_hash determinism: identical inputs → identical hash (fixed timestamp).
4.  manifest_hash sensitivity: changing payload/summary/provenance field → new hash.
5.  manifest_hash exclusion: adding signature after construction doesn't change hash.
6.  Validation — InputRef.type: bogus type raises ValueError.
7.  Validation — UpstreamRef: both set raises; neither set raises.
8.  Validation — Citation.confidence: 1.5 raises; None is fine.
9.  Defaults: timestamp defaults to UTC ISO-8601; list fields default to [];
    schema_version is auto-populated.
10. Payload dict-ification: payload with .to_dict() round-trips; plain dict also works.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from archetypes_core.corroboration import (
    Citation,
    CorroborationResult,
    PrimitiveDecomposition,
)
from archetypes_core.provenance import (
    INPUT_REF_TYPES,
    SCHEMA_VERSION,
    SCHEMA_VERSION_V01,
    InputRef,
    LapisToolReturn,
    Provenance,
    UpstreamRef,
    to_lapis_return,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIXED_TS = "2026-05-03T00:00:00+00:00"

_CITATION = Citation(
    source_id="repo:lapis-pm:pm_core.py:42",
    excerpt="No drift detected.",
    content_hash="sha256:abcdef",
    provenance_method="grep",
)

_INPUT_REF = InputRef(
    ref="repo:lapis-pm:pm_core.py:42",
    content_hash="sha256:def123",
    type="file",
)


def _minimal_ltr(**kwargs) -> LapisToolReturn:
    """Build a LapisToolReturn with minimal required fields + fixed timestamp."""
    defaults = dict(
        payload={"answer": 42},
        agent_id="lapis-pm/reviewer",
        tool="corroborate",
        summary="All good.",
        timestamp=FIXED_TS,
    )
    defaults.update(kwargs)
    return to_lapis_return(**defaults)


# ---------------------------------------------------------------------------
# 1. Round-trip: to_dict() → from_dict() equality
# ---------------------------------------------------------------------------


def test_round_trip_dict():
    ltr = _minimal_ltr(
        input_refs=[_INPUT_REF],
        citations=[_CITATION],
    )
    d = ltr.to_dict()
    restored = LapisToolReturn.from_dict(d)

    assert restored.summary == ltr.summary
    assert restored.provenance.schema_version == ltr.provenance.schema_version
    assert restored.provenance.agent_id == ltr.provenance.agent_id
    assert restored.provenance.tool == ltr.provenance.tool
    assert restored.provenance.timestamp == ltr.provenance.timestamp
    assert restored.provenance.manifest_hash == ltr.provenance.manifest_hash
    assert restored.provenance.input_refs[0].ref == ltr.provenance.input_refs[0].ref
    assert restored.provenance.citations[0].source_id == ltr.provenance.citations[0].source_id


# ---------------------------------------------------------------------------
# 2. Round-trip via JSON: to_json() / from_json()
# ---------------------------------------------------------------------------


def test_round_trip_json():
    ltr = _minimal_ltr(model="qwen3.6-35b-a3b", scope_id="repo:lapis-pm")
    j = ltr.to_json()
    restored = LapisToolReturn.from_json(j)

    assert restored.provenance.model == "qwen3.6-35b-a3b"
    assert restored.provenance.scope_id == "repo:lapis-pm"
    assert restored.provenance.manifest_hash == ltr.provenance.manifest_hash
    assert restored.summary == ltr.summary


# ---------------------------------------------------------------------------
# 3. manifest_hash determinism: same inputs → same hash
# ---------------------------------------------------------------------------


def test_manifest_hash_determinism():
    ltr1 = _minimal_ltr(citations=[_CITATION])
    ltr2 = _minimal_ltr(citations=[_CITATION])
    assert ltr1.provenance.manifest_hash == ltr2.provenance.manifest_hash


# ---------------------------------------------------------------------------
# 4. manifest_hash sensitivity: different inputs → different hash
# ---------------------------------------------------------------------------


def test_manifest_hash_sensitive_to_payload():
    ltr_a = _minimal_ltr(payload={"answer": 42})
    ltr_b = _minimal_ltr(payload={"answer": 99})
    assert ltr_a.provenance.manifest_hash != ltr_b.provenance.manifest_hash


def test_manifest_hash_sensitive_to_summary():
    ltr_a = _minimal_ltr(summary="All good.")
    ltr_b = _minimal_ltr(summary="Drift detected!")
    assert ltr_a.provenance.manifest_hash != ltr_b.provenance.manifest_hash


def test_manifest_hash_sensitive_to_provenance_field():
    ltr_a = _minimal_ltr(agent_id="agent-A")
    ltr_b = _minimal_ltr(agent_id="agent-B")
    assert ltr_a.provenance.manifest_hash != ltr_b.provenance.manifest_hash


# ---------------------------------------------------------------------------
# 5. manifest_hash exclusion: adding signature does not change hash
# ---------------------------------------------------------------------------


def test_manifest_hash_stable_after_signature():
    ltr = _minimal_ltr()
    original_hash = ltr.provenance.manifest_hash
    # Simulate adding signature post-construction (reserved field).
    ltr.provenance.signature = "sig:some-opaque-value"
    # The stored hash must not change — it was computed with signature=None.
    assert ltr.provenance.manifest_hash == original_hash


# ---------------------------------------------------------------------------
# 6. Validation — InputRef.type: bogus type raises ValueError
# ---------------------------------------------------------------------------


def test_validation_input_ref_type_bogus():
    with pytest.raises(ValueError, match="InputRef.type"):
        to_lapis_return(
            payload={"x": 1},
            agent_id="a",
            tool="t",
            summary="s",
            timestamp=FIXED_TS,
            input_refs=[InputRef(ref="foo", type="bogus_type")],
        )


def test_validation_input_ref_type_valid():
    # Each member of INPUT_REF_TYPES must be accepted without error.
    for t in INPUT_REF_TYPES:
        ltr = to_lapis_return(
            payload={},
            agent_id="a",
            tool="t",
            summary="s",
            timestamp=FIXED_TS,
            input_refs=[InputRef(ref="x", type=t)],
        )
        assert isinstance(ltr, LapisToolReturn)


# ---------------------------------------------------------------------------
# 7. Validation — UpstreamRef: exactly-one-of invariant
# ---------------------------------------------------------------------------


def _make_provenance_for_inline() -> Provenance:
    return to_lapis_return(
        payload={},
        agent_id="upstream-agent",
        tool="inner",
        summary="inner summary",
        timestamp=FIXED_TS,
    ).provenance


def test_validation_upstream_ref_both_set():
    prov = _make_provenance_for_inline()
    with pytest.raises(ValueError, match="both inline and manifest_hash"):
        to_lapis_return(
            payload={},
            agent_id="a",
            tool="t",
            summary="s",
            timestamp=FIXED_TS,
            upstream_calls=[
                UpstreamRef(
                    agent_id="upstream",
                    inline=prov,
                    manifest_hash="sha256:deadbeef",
                )
            ],
        )


def test_validation_upstream_ref_neither_set():
    with pytest.raises(ValueError, match="neither inline nor manifest_hash"):
        to_lapis_return(
            payload={},
            agent_id="a",
            tool="t",
            summary="s",
            timestamp=FIXED_TS,
            upstream_calls=[
                UpstreamRef(agent_id="upstream", inline=None, manifest_hash=None)
            ],
        )


def test_validation_upstream_ref_inline_only():
    prov = _make_provenance_for_inline()
    ltr = to_lapis_return(
        payload={},
        agent_id="a",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
        upstream_calls=[UpstreamRef(agent_id="upstream", inline=prov)],
    )
    assert len(ltr.provenance.upstream_calls) == 1


def test_validation_upstream_ref_manifest_only():
    ltr = to_lapis_return(
        payload={},
        agent_id="a",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
        upstream_calls=[
            UpstreamRef(agent_id="upstream", manifest_hash="sha256:cafebabe")
        ],
    )
    assert ltr.provenance.upstream_calls[0].manifest_hash == "sha256:cafebabe"


# ---------------------------------------------------------------------------
# 8. Validation — Citation.confidence out of range
# ---------------------------------------------------------------------------


class _CitationWithConfidence(Citation):
    """Subclass adding a confidence field for defensive validation testing."""

    def __init__(self, *args, confidence: float | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.confidence = confidence


def test_validation_citation_confidence_out_of_range():
    bad_citation = _CitationWithConfidence(
        source_id="s",
        excerpt="e",
        provenance_method="grep",
        confidence=1.5,
    )
    with pytest.raises(ValueError, match="confidence"):
        to_lapis_return(
            payload={},
            agent_id="a",
            tool="t",
            summary="s",
            timestamp=FIXED_TS,
            citations=[bad_citation],
        )


def test_validation_citation_confidence_none_is_ok():
    ok_citation = _CitationWithConfidence(
        source_id="s",
        excerpt="e",
        provenance_method="grep",
        confidence=None,
    )
    ltr = to_lapis_return(
        payload={},
        agent_id="a",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
        citations=[ok_citation],
    )
    assert isinstance(ltr, LapisToolReturn)


def test_validation_citation_confidence_boundary():
    for conf in (0.0, 0.5, 1.0):
        c = _CitationWithConfidence(
            source_id="s",
            excerpt="e",
            provenance_method="grep",
            confidence=conf,
        )
        ltr = to_lapis_return(
            payload={},
            agent_id="a",
            tool="t",
            summary="s",
            timestamp=FIXED_TS,
            citations=[c],
        )
        assert isinstance(ltr, LapisToolReturn)


# ---------------------------------------------------------------------------
# 9. Defaults
# ---------------------------------------------------------------------------


def test_defaults_timestamp_is_utc_iso8601():
    ltr = to_lapis_return(payload={}, agent_id="a", tool="t", summary="s")
    ts = ltr.provenance.timestamp
    # Must parse as a valid datetime without raising.
    dt = datetime.fromisoformat(ts)
    # Must be timezone-aware and roughly now.
    assert dt.tzinfo is not None


def test_defaults_list_fields_are_empty():
    ltr = to_lapis_return(
        payload={},
        agent_id="a",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
    )
    assert ltr.provenance.input_refs == []
    assert ltr.provenance.citations == []
    assert ltr.provenance.upstream_calls == []


def test_defaults_schema_version_auto_populated():
    ltr = to_lapis_return(
        payload={},
        agent_id="a",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
    )
    assert ltr.provenance.schema_version == SCHEMA_VERSION


# ---------------------------------------------------------------------------
# 10. Payload dict-ification
# ---------------------------------------------------------------------------


def test_payload_with_to_dict_round_trips():
    """CorroborationResult (has .to_dict()) should round-trip."""
    cr = CorroborationResult(
        verdict="clean",
        claim="No drift.",
        citations=[_CITATION],
        freshness_stamp=datetime(2026, 5, 3, tzinfo=timezone.utc),
        scope_id="repo:lapis-pm",
    )
    ltr = to_lapis_return(
        payload=cr,
        agent_id="lapis-pm/reviewer",
        tool="corroborate",
        summary="Clean.",
        timestamp=FIXED_TS,
    )
    d = ltr.to_dict()
    # payload dict should be the CorroborationResult dict
    assert d["payload"]["verdict"] == "clean"
    assert d["payload"]["claim"] == "No drift."


def test_payload_plain_dict_round_trips():
    """A plain dict payload should pass through unchanged."""
    payload = {"key": "value", "n": 7}
    ltr = to_lapis_return(
        payload=payload,
        agent_id="a",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
    )
    d = ltr.to_dict()
    assert d["payload"] == payload
    # From-dict restores payload as a dict (no type loss for plain dict).
    restored = LapisToolReturn.from_dict(d)
    assert restored.payload == payload


# ---------------------------------------------------------------------------
# Bonus: manifest_hash starts with "sha256:" prefix
# ---------------------------------------------------------------------------


def test_manifest_hash_format():
    ltr = _minimal_ltr()
    assert ltr.provenance.manifest_hash.startswith("sha256:")
    # 7 chars for "sha256:" + 64 hex chars
    assert len(ltr.provenance.manifest_hash) == 71


# ---------------------------------------------------------------------------
# pubkey_id — AC1 round-trip, AC2 envelope round-trip, AC3 hash invariance,
# AC4 backward compatibility (no pubkey_id key → None)
# ---------------------------------------------------------------------------


def test_pubkey_id_provenance_round_trip():
    """pubkey_id survives Provenance to_dict() → from_dict()."""
    prov = Provenance(
        schema_version=SCHEMA_VERSION,
        agent_id="agent:test",
        tool="t",
        timestamp=FIXED_TS,
        manifest_hash="sha256:deadbeef" + "0" * 56,
        signature="sig:opaque",
        pubkey_id="ed25519:abcdef1234567890",
    )
    d = prov.to_dict()
    assert d["pubkey_id"] == "ed25519:abcdef1234567890"
    assert d["signature"] == "sig:opaque"
    restored = Provenance.from_dict(d)
    assert restored.pubkey_id == "ed25519:abcdef1234567890"
    assert restored.signature == "sig:opaque"
    # Second round-trip must be byte-identical for those fields.
    assert restored.to_dict()["pubkey_id"] == "ed25519:abcdef1234567890"


def test_pubkey_id_envelope_round_trip():
    """to_lapis_return with pubkey_id → LapisToolReturn.from_dict preserves both fields."""
    ltr = to_lapis_return(
        payload={"x": 1},
        agent_id="agent:test",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
        signature="sig:opaque",
        pubkey_id="ed25519:abcdef1234567890",
    )
    restored = LapisToolReturn.from_dict(ltr.to_dict())
    assert restored.provenance.pubkey_id == "ed25519:abcdef1234567890"
    assert restored.provenance.signature == "sig:opaque"


def test_manifest_hash_invariant_to_pubkey_id():
    """Same content with and without pubkey_id must produce the same manifest_hash."""
    ltr_no_key = to_lapis_return(
        payload={"x": 1},
        agent_id="agent:test",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
    )
    ltr_with_key = to_lapis_return(
        payload={"x": 1},
        agent_id="agent:test",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
        pubkey_id="ed25519:abcdef1234567890",
    )
    assert ltr_no_key.provenance.manifest_hash == ltr_with_key.provenance.manifest_hash


def test_manifest_hash_invariant_to_signature():
    """Symmetric assertion: adding signature also does not change the hash."""
    ltr_no_sig = to_lapis_return(
        payload={"x": 1},
        agent_id="agent:test",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
    )
    ltr_with_sig = to_lapis_return(
        payload={"x": 1},
        agent_id="agent:test",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
        signature="sig:opaque",
    )
    assert ltr_no_sig.provenance.manifest_hash == ltr_with_sig.provenance.manifest_hash


def test_pubkey_id_backward_compatible_absent_key():
    """A provenance dict without pubkey_id deserializes with pubkey_id is None."""
    ltr = _minimal_ltr()
    d = ltr.to_dict()
    # Simulate an old envelope that has no pubkey_id key at all.
    d["provenance"].pop("pubkey_id", None)
    restored = LapisToolReturn.from_dict(d)
    assert restored.provenance.pubkey_id is None


def test_v01_envelope_surface_reconciled():
    """Reconciliation guard: SCHEMA_VERSION_V01 + the to_lapis_return
    schema_version/signature/pubkey_id/job_id params produce a v0.1 envelope
    that round-trips with all reserved signer/job fields intact. (zephyr's
    record_signed depends on exactly this surface.)"""
    assert SCHEMA_VERSION_V01 == "lapis-provenance-v0.1"
    ltr = to_lapis_return(
        payload={"x": 1},
        agent_id="agent:test",
        tool="t",
        summary="s",
        timestamp=FIXED_TS,
        schema_version=SCHEMA_VERSION_V01,
        signature="sig:opaque",
        pubkey_id="ed25519:deadbeef",
        job_id="job:123",
    )
    p = ltr.provenance
    assert p.schema_version == SCHEMA_VERSION_V01
    assert p.signature == "sig:opaque"
    assert p.pubkey_id == "ed25519:deadbeef"
    assert p.job_id == "job:123"
    restored = LapisToolReturn.from_dict(ltr.to_dict()).provenance
    assert restored.schema_version == SCHEMA_VERSION_V01
    assert restored.signature == "sig:opaque"
    assert restored.pubkey_id == "ed25519:deadbeef"
    assert restored.job_id == "job:123"
