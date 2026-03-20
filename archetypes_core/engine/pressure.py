"""
Situation Pressure → T/C/V Modifier Computation

Converts active situation primitives into modifiers that adjust the
T/C/V engine's scaling factors and character primitive weights.

Adapted from the SimulationBody pressure computation pattern in the
Archetypal Intelligence framework.
"""

from dataclasses import dataclass, field

from archetypes_core.situations import SITUATIONS


# Intensity → scale modifier mapping
INTENSITY_MODIFIERS = {
    "low": 1.0,
    "moderate": 1.15,
    "high": 1.3,
    "extreme": 1.5,
}

# Shadow trigger boost per intensity level
SHADOW_BOOST = {
    "low": 0.0,
    "moderate": 0.05,
    "high": 0.10,
    "extreme": 0.20,
}


@dataclass
class TCVModifiers:
    """Modifiers derived from active situation primitives."""
    t_scale_modifier: float = 1.0
    c_scale_modifier: float = 1.0
    v_scale_modifier: float = 1.0
    shadow_trigger_boost: float = 0.0
    weight_amplifications: dict[str, float] = field(default_factory=dict)

    def describe(self) -> str:
        parts = []
        if self.t_scale_modifier != 1.0:
            parts.append(f"T×{self.t_scale_modifier:.2f}")
        if self.c_scale_modifier != 1.0:
            parts.append(f"C×{self.c_scale_modifier:.2f}")
        if self.v_scale_modifier != 1.0:
            parts.append(f"V×{self.v_scale_modifier:.2f}")
        if self.shadow_trigger_boost > 0:
            parts.append(f"shadow+{self.shadow_trigger_boost:.2f}")
        if self.weight_amplifications:
            parts.append(f"{len(self.weight_amplifications)} primitives amplified")
        return ", ".join(parts) if parts else "no modifiers"


def compute_modifiers(situation_ids: list[str]) -> TCVModifiers:
    """
    Convert a list of active situation IDs into T/C/V modifiers.

    Logic:
    - Each situation's intensity determines scale modifier magnitude
    - Pressure targets identify primitives whose weights should be amplified
    - Shadow activators contribute to shadow trigger boost
    - Multiple situations compound (multiplicative for scales, additive for shadow boost)
    - Primitives under pressure get a weight amplification factor (1.2 per targeting situation)
    """
    mods = TCVModifiers()

    for sid in situation_ids:
        sit = SITUATIONS.get(sid)
        if not sit:
            continue

        intensity = sit.get("intensity", "moderate")
        intensity_mod = INTENSITY_MODIFIERS.get(intensity, 1.0)

        # Scale modifiers compound multiplicatively
        # Situations generally increase tension and volatility, may dampen complementarity
        mods.t_scale_modifier *= intensity_mod
        mods.v_scale_modifier *= intensity_mod
        # Complementarity is slightly dampened under pressure (pressure tests bonds)
        mods.c_scale_modifier *= (1.0 / (1.0 + (intensity_mod - 1.0) * 0.3))

        # Shadow trigger boost is additive
        mods.shadow_trigger_boost += SHADOW_BOOST.get(intensity, 0.0)

        # Primitives targeted by this situation get amplified
        for pt in sit.get("pressure_targets", []):
            pid = pt["primitive_id"]
            # Each targeting situation adds 20% weight boost
            current = mods.weight_amplifications.get(pid, 1.0)
            mods.weight_amplifications[pid] = current * 1.2

    return mods


def apply_weight_amplifications(
    characters: list[dict],
    amplifications: dict[str, float],
) -> list[dict]:
    """
    Create modified copies of characters with amplified primitive weights.

    Characters are deep-copied. Weights are multiplied by amplification factors,
    then renormalized so primaries still sum to ~1.0.

    Returns new character dicts — does not mutate originals.
    """
    import copy
    modified = []

    for char in characters:
        new_char = copy.deepcopy(char)

        # Amplify primary weights
        total = 0.0
        for p in new_char["primary"]:
            amp = amplifications.get(p["primitive_id"], 1.0)
            p["weight"] *= amp
            total += p["weight"]

        # Renormalize primaries to sum to 1.0
        if total > 0:
            for p in new_char["primary"]:
                p["weight"] = round(p["weight"] / total, 4)

        # Shadow weights: amplify but don't renormalize (they're independent)
        for s in new_char.get("shadow", []):
            amp = amplifications.get(s["primitive_id"], 1.0)
            s["weight"] = round(s["weight"] * amp, 4)

        modified.append(new_char)

    return modified
