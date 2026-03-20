"""
Archetypal Intelligence — Lineage Model

A Lineage tracks a single archetype as it travels across cultural traditions.
Each Variant is the archetype reimagined within a specific tradition/era,
decomposed into behavioral primitives. Comparing variants reveals:

  - The archetype's irreducible core (what persists across all traditions)
  - Each tradition's fingerprint (what it consistently adds or removes)
  - The trajectory of transformation (how meaning shifts through cultural time)
"""

from dataclasses import dataclass, field


@dataclass
class Variant:
    """One version of an archetype within a specific tradition."""
    id: str                         # e.g. "prometheus-aeschylus"
    name: str                       # e.g. "Aeschylus's Prometheus"
    tradition: str                  # e.g. "Greek Tragedy"
    era: str                        # e.g. "~450 BCE"
    source_work: str                # e.g. "Prometheus Bound"
    backstory: str                  # The backstory text for decomposition
    primary: list[dict] = field(default_factory=list)   # Decomposed primaries
    shadow: list[dict] = field(default_factory=list)    # Decomposed shadows

    def primitive_weights(self) -> dict[str, float]:
        """Return {primitive_id: weight} for all primaries."""
        return {p["primitive_id"]: p["weight"] for p in self.primary}

    def shadow_weights(self) -> dict[str, float]:
        """Return {primitive_id: weight} for all shadows."""
        return {s["primitive_id"]: s["weight"] for s in self.shadow}

    def to_engine_format(self) -> dict:
        """Return dict compatible with engine.compute_pair_scores()."""
        return {
            "id": self.id,
            "name": self.name,
            "genre": self.tradition,
            "genre_detail": f"{self.tradition}, {self.era}",
            "backstory": self.backstory,
            "primary": self.primary,
            "shadow": self.shadow,
        }


@dataclass
class Lineage:
    """An archetype tracked across multiple traditions."""
    id: str                         # e.g. "prometheus"
    name: str                       # e.g. "Prometheus"
    description: str                # What this archetype carries
    variants: list[Variant] = field(default_factory=list)

    def variant_by_id(self, variant_id: str) -> Variant | None:
        for v in self.variants:
            if v.id == variant_id:
                return v
        return None

    def traditions(self) -> list[str]:
        """All unique traditions in this lineage."""
        return list(dict.fromkeys(v.tradition for v in self.variants))

    def chronological(self) -> list[Variant]:
        """Variants ordered by their position in the variants list (assumed chronological)."""
        return list(self.variants)
