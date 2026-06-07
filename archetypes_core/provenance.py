"""Lapis Provenance Schema v0 — envelope dataclasses + helper.

Implements Move 2 of the Lapis Provenance Schema v0 spec
(vault PR #87, Lapis/Architecture-Provenance-Schema-v0.md).

Adds the envelope dataclasses (InputRef, UpstreamRef, Provenance,
LapisToolReturn) and the to_lapis_return() factory helper.  Imports
Citation and PrimitiveDecomposition from archetypes_core.corroboration —
they are NOT duplicated here.

Invariants:
- This module makes NO LLM calls.
- No existing dataclass in corroboration.py is modified.
- archetypes_core remains a pure-CPU library.
- Field names match the schema doc verbatim.
- Field order in Provenance matches the schema doc declaration order.
- to_lapis_return() raises ValueError on protocol violations rather than
  silently constructing invalid envelopes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from archetypes_core.corroboration import Citation, PrimitiveDecomposition

# ---------------------------------------------------------------------------
# Schema version constant
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "lapis-provenance-v0"
SCHEMA_VERSION_V01 = "lapis-provenance-v0.1"  # activates reserved signature + job_id slots

# ---------------------------------------------------------------------------
# Closed enum for InputRef.type at v0
# Additions in v1 require a schema_version bump.
# ---------------------------------------------------------------------------

INPUT_REF_TYPES: frozenset[str] = frozenset(
    {
        "prompt",
        "file",
        "tool_result",
        "claim",
        "corpus_snapshot",
        "freshness_budget",
    }
)


# ---------------------------------------------------------------------------
# InputRef
# ---------------------------------------------------------------------------


@dataclass
class InputRef:
    """Reference to a single input that contributed to the tool's output."""

    ref: str
    content_hash: str | None = None
    type: str = "file"  # must be in INPUT_REF_TYPES; validated by to_lapis_return()

    def to_dict(self) -> dict[str, Any]:
        return {
            "ref": self.ref,
            "content_hash": self.content_hash,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "InputRef":
        return cls(
            ref=d["ref"],
            content_hash=d.get("content_hash"),
            type=d.get("type", "file"),
        )


# ---------------------------------------------------------------------------
# UpstreamRef
# ---------------------------------------------------------------------------


@dataclass
class UpstreamRef:
    """Polymorphic upstream-call reference.

    Exactly one of {inline, manifest_hash} must be populated.
    - inline: full Provenance inlined (for short / local upstream calls).
    - manifest_hash: opaque hash pointing to a separately-stored Provenance.
    """

    agent_id: str
    inline: "Provenance | None" = None
    manifest_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "inline": self.inline.to_dict() if self.inline is not None else None,
            "manifest_hash": self.manifest_hash,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UpstreamRef":
        return cls(
            agent_id=d["agent_id"],
            inline=(
                Provenance.from_dict(d["inline"])
                if d.get("inline") is not None
                else None
            ),
            manifest_hash=d.get("manifest_hash"),
        )


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


@dataclass
class Provenance:
    """Full provenance record for a single tool invocation.

    Field order matches the schema doc declaration order (§"The schema").
    Required fields have no default; optional / reserved fields default to
    None or empty list.
    """

    schema_version: str
    agent_id: str
    tool: str
    timestamp: str                                           # ISO-8601 UTC
    manifest_hash: str                                       # populated by to_lapis_return()
    scope_id: str | None = None
    model: str | None = None
    prompt_hash: str | None = None
    input_refs: list[InputRef] = field(default_factory=list)
    upstream_calls: list[UpstreamRef] = field(default_factory=list)
    primitive_decomposition: PrimitiveDecomposition | None = None
    citations: list[Citation] = field(default_factory=list)
    signature: str | None = None                             # reserved post-v0
    pubkey_id: str | None = None                             # reserved post-v0; signer key identity
    history_layer_hash: str | None = None                   # reserved post-v0
    job_id: str | None = None                               # reserved post-v0

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "agent_id": self.agent_id,
            "tool": self.tool,
            "timestamp": self.timestamp,
            "manifest_hash": self.manifest_hash,
            "scope_id": self.scope_id,
            "model": self.model,
            "prompt_hash": self.prompt_hash,
            "input_refs": [ir.to_dict() for ir in self.input_refs],
            "upstream_calls": [uc.to_dict() for uc in self.upstream_calls],
            "primitive_decomposition": (
                self.primitive_decomposition.to_dict()
                if self.primitive_decomposition is not None
                else None
            ),
            "citations": [c.to_dict() for c in self.citations],
            "signature": self.signature,
            "pubkey_id": self.pubkey_id,
            "history_layer_hash": self.history_layer_hash,
            "job_id": self.job_id,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Provenance":
        return cls(
            schema_version=d["schema_version"],
            agent_id=d["agent_id"],
            tool=d["tool"],
            timestamp=d["timestamp"],
            manifest_hash=d["manifest_hash"],
            scope_id=d.get("scope_id"),
            model=d.get("model"),
            prompt_hash=d.get("prompt_hash"),
            input_refs=[InputRef.from_dict(ir) for ir in d.get("input_refs", [])],
            upstream_calls=[
                UpstreamRef.from_dict(uc) for uc in d.get("upstream_calls", [])
            ],
            primitive_decomposition=(
                PrimitiveDecomposition.from_dict(d["primitive_decomposition"])
                if d.get("primitive_decomposition") is not None
                else None
            ),
            citations=[Citation.from_dict(c) for c in d.get("citations", [])],
            signature=d.get("signature"),
            pubkey_id=d.get("pubkey_id"),
            history_layer_hash=d.get("history_layer_hash"),
            job_id=d.get("job_id"),
        )


# ---------------------------------------------------------------------------
# LapisToolReturn
# ---------------------------------------------------------------------------


@dataclass
class LapisToolReturn:
    """Envelope wrapping any tool's payload with Lapis provenance.

    payload dict-ification convention:
    - If payload has a .to_dict() method (e.g. CorroborationResult), it is
      called to produce the dict representation in to_dict() / to_json().
    - If payload is already a plain dict or other JSON-serializable value,
      it is passed through unchanged.
    This lets dataclasses plug in without adaptation.
    """

    payload: Any
    summary: str
    provenance: Provenance

    def to_dict(self) -> dict[str, Any]:
        if hasattr(self.payload, "to_dict"):
            payload_repr = self.payload.to_dict()
        else:
            payload_repr = self.payload
        return {
            "payload": payload_repr,
            "summary": self.summary,
            "provenance": self.provenance.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "LapisToolReturn":
        return cls(
            payload=d["payload"],
            summary=d["summary"],
            provenance=Provenance.from_dict(d["provenance"]),
        )

    @classmethod
    def from_json(cls, s: str) -> "LapisToolReturn":
        return cls.from_dict(json.loads(s))


# ---------------------------------------------------------------------------
# _canonical_json — deterministic serialization for manifest_hash
# ---------------------------------------------------------------------------


def _default_encoder(obj: Any) -> Any:
    """JSON default encoder for _canonical_json.

    - Dataclasses / objects with .to_dict(): delegate.
    - datetime: .isoformat().
    - Everything else: let json.dumps raise naturally.
    """
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _canonical_json(obj: Any) -> str:
    """Deterministic JSON serialization used for manifest_hash computation.

    Rules:
    - Keys sorted alphabetically (sort_keys=True).
    - No whitespace (separators=(',', ':')).
    - Floats serialized via repr() — Python's shortest round-trip form,
      stable across CPython versions.
    - Datetimes / dataclasses are .isoformat()'d / .to_dict()'d before
      serialization via _default_encoder.

    Guarantee: serializing the same logical content twice yields bytes-identical
    JSON → same hash.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=_default_encoder)


# ---------------------------------------------------------------------------
# to_lapis_return() — the factory helper
# ---------------------------------------------------------------------------


def to_lapis_return(
    payload: Any,
    *,
    agent_id: str,
    tool: str,
    summary: str,
    model: str | None = None,
    prompt_hash: str | None = None,
    input_refs: list[InputRef] | None = None,
    citations: list[Citation] | None = None,
    primitive_decomposition: PrimitiveDecomposition | None = None,
    upstream_calls: list[UpstreamRef] | None = None,
    scope_id: str | None = None,
    timestamp: "datetime | str | None" = None,
    schema_version: str = SCHEMA_VERSION,
    signature: str | None = None,
    pubkey_id: str | None = None,
    job_id: str | None = None,
) -> LapisToolReturn:
    """Wrap an existing payload in a v0-conformant LapisToolReturn envelope.

    Behavior:
    1. Defaults timestamp to datetime.now(timezone.utc).isoformat() if not given.
       Accepts both datetime (converted via .isoformat()) and pre-formatted
       ISO-8601 strings.
    2. Defaults all list fields to [] if None.
    3. Populates schema_version = SCHEMA_VERSION.
    4. Validates (raises ValueError with a clear message on any violation):
       - Each InputRef.type is in INPUT_REF_TYPES.
       - Each UpstreamRef has exactly one of {inline, manifest_hash} populated.
       - Each Citation.confidence, when not None, is a float in [0, 1].
         (confidence is not a field on Citation at v0 — validated defensively
          if a future subclass adds it.)
    5. Computes manifest_hash over payload + provenance (with manifest_hash
       and signature zeroed) and assigns it to Provenance.manifest_hash.
    6. Returns the assembled LapisToolReturn.

    Raises:
        ValueError: On any protocol violation (invalid InputRef.type,
            UpstreamRef not-exactly-one-of, Citation.confidence out of range).
    """
    # 1. Resolve timestamp
    if timestamp is None:
        ts = datetime.now(timezone.utc).isoformat()
    elif isinstance(timestamp, datetime):
        ts = timestamp.isoformat()
    else:
        ts = timestamp  # already a string

    # 2. Default list fields
    resolved_input_refs = input_refs if input_refs is not None else []
    resolved_citations = citations if citations is not None else []
    resolved_upstream_calls = upstream_calls if upstream_calls is not None else []

    # 4a. Validate InputRef.type
    for ir in resolved_input_refs:
        if ir.type not in INPUT_REF_TYPES:
            raise ValueError(
                f"InputRef.type {ir.type!r} is not in INPUT_REF_TYPES. "
                f"Valid values: {sorted(INPUT_REF_TYPES)}"
            )

    # 4b. Validate UpstreamRef exactly-one-of
    for uc in resolved_upstream_calls:
        has_inline = uc.inline is not None
        has_manifest = uc.manifest_hash is not None
        if has_inline and has_manifest:
            raise ValueError(
                f"UpstreamRef(agent_id={uc.agent_id!r}) has both inline and "
                "manifest_hash set; exactly one must be populated."
            )
        if not has_inline and not has_manifest:
            raise ValueError(
                f"UpstreamRef(agent_id={uc.agent_id!r}) has neither inline nor "
                "manifest_hash set; exactly one must be populated."
            )

    # 4c. Validate Citation.confidence if present (defensive — not on Citation at v0)
    for c in resolved_citations:
        conf = getattr(c, "confidence", None)
        if conf is not None:
            if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
                raise ValueError(
                    f"Citation.confidence {conf!r} is out of range [0, 1]."
                )

    # 3 & 5. Build provenance with manifest_hash placeholder, then compute hash.
    provenance = Provenance(
        schema_version=schema_version,
        agent_id=agent_id,
        tool=tool,
        timestamp=ts,
        manifest_hash="",  # placeholder; filled after hash computation
        scope_id=scope_id,
        model=model,
        prompt_hash=prompt_hash,
        input_refs=resolved_input_refs,
        upstream_calls=resolved_upstream_calls,
        primitive_decomposition=primitive_decomposition,
        citations=resolved_citations,
        signature=signature,
        pubkey_id=pubkey_id,
        history_layer_hash=None,
        job_id=job_id,
    )

    # Compute manifest_hash over payload + provenance with manifest_hash and
    # signature zeroed.  We serialize provenance as its dict with those two
    # keys removed so that adding a signature later does not invalidate the hash.
    prov_dict = provenance.to_dict()
    del prov_dict["manifest_hash"]
    del prov_dict["signature"]
    del prov_dict["pubkey_id"]

    if hasattr(payload, "to_dict"):
        payload_dict = payload.to_dict()
    else:
        payload_dict = payload

    hashable = _canonical_json({"payload": payload_dict, "provenance": prov_dict, "summary": summary})
    digest = hashlib.sha256(hashable.encode()).hexdigest()
    provenance.manifest_hash = f"sha256:{digest}"

    return LapisToolReturn(
        payload=payload,
        summary=summary,
        provenance=provenance,
    )
