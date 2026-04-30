"""World-scale primitive types for substrate composition.

Worlds decompose into primitives at world-scale.  This mirrors "characters
are compositions of Archetypal Intelligence primitives" but applied at the
substrate layer.

Two primitive classes:

1. ThemePrimitive — the substantive primitive class.  Entities (deities,
   factions, heroes) are *compositions* of themes.

2. IsomorphicLinkPrimitive — encodes "in this world, domain A's dynamics
   mirror domain B's dynamics via shared primitive Z" (e.g. biological
   rhythm ↔ divine internal state ↔ environmental cycle via 'rhythmic
   process as expression of internal state').

q1 resolution (2026-04-30): isomorphic-link primitives are a composition
pattern over existing Archetypal Intelligence primitives applied across
multiple substrate domains.  They are retained as a named class here for
v0 tractability; the structure is small enough to revise non-disruptively
in v0.next if shaping concludes the named class is unnecessary.

Both classes resolve to a ``WorldPrimitive`` union type, and
``WorldPrimitiveComposition`` assembles a world's spirit as a weighted
sequence of those primitives.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal, Union


# ---------------------------------------------------------------------------
# PrimitiveRef — lightweight reference into the AI primitive catalog
# ---------------------------------------------------------------------------


@dataclass
class PrimitiveRef:
    """Lightweight reference to an Archetypal Intelligence primitive.

    Keeps isomorphic-link primitives from embedding full PrimitiveCard
    objects — adapters resolve the ref against the catalog when needed.
    """

    primitive_id: str          # matches PrimitiveCard.card_id in the catalog
    display_name: str          # human-readable label for diagnostics

    def to_dict(self) -> dict[str, str]:
        return {"primitive_id": self.primitive_id, "display_name": self.display_name}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PrimitiveRef":
        return cls(primitive_id=d["primitive_id"], display_name=d["display_name"])


# ---------------------------------------------------------------------------
# ThemePrimitive
# ---------------------------------------------------------------------------


@dataclass
class ThemePrimitive:
    """A thematic building block at world-scale.

    Themes are the substantive primitive class: deities, factions, and
    heroes are compositions of themes.

    Attributes:
        theme_id: Stable identifier for this theme within the world.
        name: Short, evocative human-readable name.
        description: Longer description of how this theme manifests.
        weight: Relative salience in the world's spirit (0.0–1.0).
        tags: Optional free-form tags for faceting (e.g. ["death", "cycle"]).
    """

    kind: Literal["theme"] = field(default="theme", init=False)
    theme_id: str
    name: str
    description: str
    weight: float = 1.0
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "theme_id": self.theme_id,
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ThemePrimitive":
        obj = cls(
            theme_id=d["theme_id"],
            name=d["name"],
            description=d["description"],
            weight=d.get("weight", 1.0),
            tags=d.get("tags", []),
        )
        return obj


# ---------------------------------------------------------------------------
# IsomorphicLinkPrimitive
# ---------------------------------------------------------------------------


@dataclass
class IsomorphicLinkPrimitive:
    """Encodes a structural isomorphism across substrate domains.

    "In this world, domain A's dynamics mirror domain B's dynamics via
    shared primitive Z."  Example: biological rhythm ↔ divine internal
    state ↔ environmental cycle via 'rhythmic process as expression of
    internal state'.

    This is a composition pattern over existing Archetypal Intelligence
    primitives applied across multiple substrate domains (q1 resolution).
    The named class is a v0 convenience for tractability.

    Attributes:
        link_id: Stable identifier for this isomorphic link.
        domains: Two or more domain labels that mirror each other
                 (e.g. ["biological", "divine", "environmental"]).
        shared_primitive: The AI primitive that is expressed isomorphically
                          across all listed domains.
        manifestation_examples: Concrete examples of the isomorphism in play,
                                one per domain is sufficient.
        weight: Relative salience in the world's spirit (0.0–1.0).
    """

    kind: Literal["isomorphic_link"] = field(default="isomorphic_link", init=False)
    link_id: str
    domains: list[str]
    shared_primitive: PrimitiveRef
    manifestation_examples: list[str]
    weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "link_id": self.link_id,
            "domains": self.domains,
            "shared_primitive": self.shared_primitive.to_dict(),
            "manifestation_examples": self.manifestation_examples,
            "weight": self.weight,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "IsomorphicLinkPrimitive":
        obj = cls(
            link_id=d["link_id"],
            domains=d["domains"],
            shared_primitive=PrimitiveRef.from_dict(d["shared_primitive"]),
            manifestation_examples=d["manifestation_examples"],
            weight=d.get("weight", 1.0),
        )
        return obj


# ---------------------------------------------------------------------------
# Union type
# ---------------------------------------------------------------------------

WorldPrimitive = Union[ThemePrimitive, IsomorphicLinkPrimitive]


def world_primitive_from_dict(d: dict[str, Any]) -> WorldPrimitive:
    """Deserialize a WorldPrimitive from a plain dict (e.g. from JSON or SQLite)."""
    kind = d.get("kind")
    if kind == "theme":
        return ThemePrimitive.from_dict(d)
    if kind == "isomorphic_link":
        return IsomorphicLinkPrimitive.from_dict(d)
    raise ValueError(f"Unknown world primitive kind: {kind!r}")


def world_primitive_to_dict(p: WorldPrimitive) -> dict[str, Any]:
    """Serialize a WorldPrimitive to a plain dict."""
    return p.to_dict()


# ---------------------------------------------------------------------------
# WorldPrimitiveComposition — a world's spirit-as-encoded
# ---------------------------------------------------------------------------


@dataclass
class WorldPrimitiveComposition:
    """An ordered, weighted collection of world primitives.

    This is the world's "spirit" as encoded by the GM.  It is GM-authored,
    not Haiku-generated.  Adapters ground corroboration calls against it.

    Attributes:
        world_id: Stable identifier for the world / campaign.
        primitives: Ordered sequence of ThemePrimitive and
                    IsomorphicLinkPrimitive entries.
        authored_at: ISO-8601 timestamp of when the GM seeded this composition.
        notes: Optional GM notes about the composition as a whole.
    """

    world_id: str
    primitives: list[WorldPrimitive]
    authored_at: str              # ISO-8601
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "world_id": self.world_id,
            "primitives": [p.to_dict() for p in self.primitives],
            "authored_at": self.authored_at,
            "notes": self.notes,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WorldPrimitiveComposition":
        return cls(
            world_id=d["world_id"],
            primitives=[world_primitive_from_dict(p) for p in d["primitives"]],
            authored_at=d["authored_at"],
            notes=d.get("notes"),
        )

    @classmethod
    def from_json(cls, s: str) -> "WorldPrimitiveComposition":
        return cls.from_dict(json.loads(s))

    # Convenience accessors
    def themes(self) -> list[ThemePrimitive]:
        return [p for p in self.primitives if isinstance(p, ThemePrimitive)]

    def isomorphic_links(self) -> list[IsomorphicLinkPrimitive]:
        return [p for p in self.primitives if isinstance(p, IsomorphicLinkPrimitive)]
