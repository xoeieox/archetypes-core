"""Cross-node corroboration primitive.

Thin orchestrator: asks the adapter for relevant substrate, asks the adapter
to score the claim against that substrate, returns the result in evidence-packet
shape.  The adapter owns all substrate-specific logic (including any LLM calls).

Invariants:
- This module makes NO LLM calls.
- CorroborationResult is evidence-packet-shaped from day 1.
- SubstrateAdapter is the cross-substrate contract; any future adapter
  (brand-voice, craftsperson, agent-OS) implements the same protocol.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Freshness budget
# ---------------------------------------------------------------------------


class FreshnessBudget(str, Enum):
    """How stale the substrate data is allowed to be.

    Adapters interpret these as policy hints; the primitive passes the budget
    through without modification.
    """

    REALTIME = "realtime"    # retrieve must go to live source
    RECENT = "recent"        # cached data from within the last ~5 minutes OK
    HOUR = "hour"            # within the last hour OK
    DAY = "day"              # within the last day OK
    ANY = "any"              # use whatever is available, no freshness gate


# ---------------------------------------------------------------------------
# Citation (SCP-shaped attribution)
# ---------------------------------------------------------------------------


@dataclass
class Citation:
    """A single attributed source reference.

    SCP-shaped: Source, Claim-fragment, Provenance.
    """

    source_id: str                   # e.g. filename, table row key, vault note path
    excerpt: str                     # the relevant fragment from the source
    content_hash: str | None = None  # sha256 of source at retrieval time; None when no snapshot captured
    provenance_method: str = ""      # how the source was located (grep, DB query, RAG, etc.)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "excerpt": self.excerpt,
            "content_hash": self.content_hash,
            "provenance_method": self.provenance_method,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Citation":
        return cls(
            source_id=d["source_id"],
            excerpt=d["excerpt"],
            content_hash=d.get("content_hash"),
            provenance_method=d["provenance_method"],
        )


# ---------------------------------------------------------------------------
# PrimitiveDecomposition (compost-routing handle)
# ---------------------------------------------------------------------------


@dataclass
class PrimitiveDecomposition:
    """Entry-time decomposition of a claim's implied primitives.

    Attached once at entry (one-time LLM cost in the adapter); never
    re-computed on access.  Enables pure-computation similarity routing
    downstream (the compost invariant: nothing is waste).
    """

    primitives: list[str]              # ordered primitive IDs or names
    weights: list[float]               # parallel weights, sum ~1.0
    decomposition_method: str          # e.g. "haiku-constrained-json", "manual"
    decomposed_at: str                 # ISO-8601 timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "primitives": self.primitives,
            "weights": self.weights,
            "decomposition_method": self.decomposition_method,
            "decomposed_at": self.decomposed_at,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PrimitiveDecomposition":
        return cls(
            primitives=d["primitives"],
            weights=d["weights"],
            decomposition_method=d["decomposition_method"],
            decomposed_at=d["decomposed_at"],
        )


# ---------------------------------------------------------------------------
# CorroborationResult (evidence-packet shape)
# ---------------------------------------------------------------------------


@dataclass
class CorroborationResult:
    """Evidence-packet shaped corroboration output.

    The schema is the cross-consumer contract: downstream consumers
    (claude-view Atmosphere panel, mem.db evidence keys, future federation)
    depend on this shape from day 1.

    All results — clean, flagged, uncertain — are persisted; none are waste.
    """

    verdict: Literal["clean", "flagged", "uncertain"]
    claim: str
    citations: list[Citation]
    freshness_stamp: datetime          # when the substrate was retrieved
    scope_id: str                      # identifies which substrate was queried
    drift_class: str | None = None     # adapter-specific classification
    notes: str | None = None           # short adapter-produced explanation
    primitive_decomposition: PrimitiveDecomposition | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "claim": self.claim,
            "citations": [c.to_dict() for c in self.citations],
            "freshness_stamp": self.freshness_stamp.isoformat(),
            "scope_id": self.scope_id,
            "drift_class": self.drift_class,
            "notes": self.notes,
            "primitive_decomposition": (
                self.primitive_decomposition.to_dict()
                if self.primitive_decomposition is not None
                else None
            ),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CorroborationResult":
        return cls(
            verdict=d["verdict"],
            claim=d["claim"],
            citations=[Citation.from_dict(c) for c in d["citations"]],
            freshness_stamp=datetime.fromisoformat(d["freshness_stamp"]),
            scope_id=d["scope_id"],
            drift_class=d.get("drift_class"),
            notes=d.get("notes"),
            primitive_decomposition=(
                PrimitiveDecomposition.from_dict(d["primitive_decomposition"])
                if d.get("primitive_decomposition") is not None
                else None
            ),
        )

    @classmethod
    def from_json(cls, s: str) -> "CorroborationResult":
        return cls.from_dict(json.loads(s))


# ---------------------------------------------------------------------------
# Substrate (opaque bag carried between retrieve → score)
# ---------------------------------------------------------------------------


@dataclass
class Substrate:
    """Opaque substrate data returned by SubstrateAdapter.retrieve.

    The primitive does not inspect the payload; it passes it straight to
    SubstrateAdapter.score.  Adapters use the payload field freely.
    """

    scope_id: str
    retrieved_at: datetime
    payload: Any                       # adapter-defined; not inspected here


# ---------------------------------------------------------------------------
# SubstrateUnavailable signal
# ---------------------------------------------------------------------------


class SubstrateUnavailable(Exception):
    """Raised by SubstrateAdapter.retrieve when the substrate cannot be reached.

    The corroborate() primitive catches this and returns verdict="uncertain".
    """

    def __init__(self, scope_id: str, reason: str) -> None:
        self.scope_id = scope_id
        self.reason = reason
        super().__init__(f"Substrate '{scope_id}' unavailable: {reason}")


# ---------------------------------------------------------------------------
# SubstrateAdapter protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class SubstrateAdapter(Protocol):
    """Cross-substrate contract.

    Any future adapter (Kyma world, lapis-pm reviewer, brand-voice,
    craftsperson, agent-OS) implements this protocol.  The primitive
    treats all adapters identically.

    LLM calls (when needed) live inside the adapter, not in the primitive.
    """

    @property
    def scope_id(self) -> str:
        """Stable identifier for this substrate (used in CorroborationResult.scope_id)."""
        ...

    def retrieve(self, claim: str, freshness: FreshnessBudget) -> Substrate:
        """Fetch the substrate data relevant to grounding the claim.

        Args:
            claim: The natural-language claim to be corroborated.
            freshness: Freshness budget — how stale the data is allowed to be.

        Returns:
            Substrate with the relevant data payload.

        Raises:
            SubstrateUnavailable: If the substrate cannot be reached or is
                entirely absent.
        """
        ...

    def score(self, claim: str, substrate: Substrate) -> CorroborationResult:
        """Score the claim against the retrieved substrate.

        Args:
            claim: The natural-language claim to be corroborated.
            substrate: As returned by retrieve().

        Returns:
            CorroborationResult with verdict, citations, and optional drift_class.
        """
        ...


# ---------------------------------------------------------------------------
# corroborate() — the primitive
# ---------------------------------------------------------------------------


def corroborate(
    claim: str,
    scope: SubstrateAdapter,
    freshness: FreshnessBudget,
) -> CorroborationResult:
    """Corroborate a claim against a substrate.

    This is a thin orchestrator.  It:
    1. Asks the adapter to retrieve relevant substrate (with the freshness budget).
    2. Asks the adapter to score the claim against that substrate.
    3. Returns the result in evidence-packet shape.

    If the substrate is unavailable the verdict is "uncertain" with an empty
    citations list and a notes field explaining the unavailability.

    Args:
        claim: The natural-language claim to be corroborated.
        scope: A SubstrateAdapter implementing retrieve() + score().
        freshness: How stale the substrate data is allowed to be.

    Returns:
        CorroborationResult — always returned, never raises.
    """
    try:
        substrate = scope.retrieve(claim, freshness)
    except SubstrateUnavailable as exc:
        return CorroborationResult(
            verdict="uncertain",
            claim=claim,
            citations=[],
            freshness_stamp=datetime.now(tz=timezone.utc),
            scope_id=exc.scope_id,
            notes=f"Substrate unavailable: {exc.reason}",
        )

    return scope.score(claim, substrate)
