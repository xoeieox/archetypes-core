"""
Archetypal Intelligence — T/C/V Pairwise Scoring

Pure computation module. No LLM calls. No web framework imports.

Computes three scores per character pair:
  T (Tension)         — opposing primitives create friction
  C (Complementarity) — synergistic primitives create mutual strength
  V (Volatility)      — shadow primitives create unpredictability

Scores are 0.0–1.0, empirically scaled so the premade roster spreads
meaningfully across the range.
"""

from archetypes_core.primitives import PRIMITIVES

# Empirical scaling factors — calibrated against all 252 party combinations.
T_SCALE = 5.0
C_SCALE = 5.0
V_SCALE = 1.5
# Untriggered shadows contribute at this fraction (shadows that aren't
# activated by the other character's primaries are mostly dormant).
V_UNTRIGGERED_DAMPEN = 0.2


def _is_tension(prim_a: str, prim_b: str) -> bool:
    """Check if two primitives are in tension (bidirectional)."""
    a = PRIMITIVES.get(prim_a, {})
    b = PRIMITIVES.get(prim_b, {})
    return prim_b in a.get("tension_with", []) or prim_a in b.get("tension_with", [])


def _is_complementary(prim_a: str, prim_b: str) -> bool:
    """Check if two primitives are complementary (bidirectional)."""
    a = PRIMITIVES.get(prim_a, {})
    b = PRIMITIVES.get(prim_b, {})
    return prim_b in a.get("complementary_with", []) or prim_a in b.get("complementary_with", [])


def compute_tension(char_a: dict, char_b: dict, *, t_scale=None) -> tuple[float, list]:
    """
    For each primary primitive pair (one from A, one from B), if they are
    in tension, contribution = weight_A * weight_B.

    Returns (score, contributing_pairs).
    """
    raw = 0.0
    contributors = []
    for pa in char_a["primary"]:
        for pb in char_b["primary"]:
            if _is_tension(pa["primitive_id"], pb["primitive_id"]):
                contribution = pa["weight"] * pb["weight"]
                raw += contribution
                contributors.append({
                    "a_primitive": pa["primitive_id"],
                    "b_primitive": pb["primitive_id"],
                    "contribution": round(contribution, 4),
                })
    score = min(raw * (t_scale or T_SCALE), 1.0)
    return round(score, 3), contributors


def compute_complementarity(char_a: dict, char_b: dict, *, c_scale=None) -> tuple[float, list]:
    """
    Same as tension but using complementary relationships.

    Returns (score, contributing_pairs).
    """
    raw = 0.0
    contributors = []
    for pa in char_a["primary"]:
        for pb in char_b["primary"]:
            if _is_complementary(pa["primitive_id"], pb["primitive_id"]):
                contribution = pa["weight"] * pb["weight"]
                raw += contribution
                contributors.append({
                    "a_primitive": pa["primitive_id"],
                    "b_primitive": pb["primitive_id"],
                    "contribution": round(contribution, 4),
                })
    score = min(raw * (c_scale or C_SCALE), 1.0)
    return round(score, 3), contributors


def compute_volatility(char_a: dict, char_b: dict, *, v_scale=None, v_dampen=None) -> tuple[float, list]:
    """
    Shadow-based scoring. For each shadow primitive in A:
      base = shadow_weight * primitive's shadow_volatility
      If B has a primary primitive that's in the shadow primitive's tension list,
      the shadow fires at full weight. Otherwise dampened.
    Then do the same for B's shadows against A's primaries.

    Returns (score, contributing_shadows).
    """
    effective_dampen = v_dampen or V_UNTRIGGERED_DAMPEN
    raw = 0.0
    contributors = []

    for char_self, char_other, label in [
        (char_a, char_b, "a_shadow"),
        (char_b, char_a, "b_shadow"),
    ]:
        for shadow in char_self.get("shadow", []):
            sid = shadow["primitive_id"]
            s_weight = shadow["weight"]
            s_vol = PRIMITIVES.get(sid, {}).get("shadow_volatility", 0.3)
            base = s_weight * s_vol

            # Check if other character's primaries would trigger this shadow
            triggers = []
            shadow_tensions = PRIMITIVES.get(sid, {}).get("tension_with", [])
            for po in char_other["primary"]:
                if po["primitive_id"] in shadow_tensions:
                    triggers.append(po["primitive_id"])

            # Triggered shadows contribute fully; untriggered ones are mostly dormant
            if triggers:
                contribution = base
            else:
                contribution = base * effective_dampen

            raw += contribution
            contributors.append({
                "source": label,
                "shadow_primitive": sid,
                "triggered_by": triggers,
                "contribution": round(contribution, 4),
            })

    score = min(raw * (v_scale or V_SCALE), 1.0)
    return round(score, 3), contributors


def compute_pair_scores(char_a: dict, char_b: dict, *, t_scale=None, c_scale=None, v_scale=None, v_dampen=None) -> dict:
    """Compute full T/C/V analysis for a character pair."""
    from archetypes_core.engine.party import classify_pair

    t, t_detail = compute_tension(char_a, char_b, t_scale=t_scale)
    c, c_detail = compute_complementarity(char_a, char_b, c_scale=c_scale)
    v, v_detail = compute_volatility(char_a, char_b, v_scale=v_scale, v_dampen=v_dampen)
    label = classify_pair(t, c, v)

    return {
        "a": char_a["id"],
        "b": char_b["id"],
        "a_name": char_a["name"],
        "b_name": char_b["name"],
        "t": t,
        "c": c,
        "v": v,
        "label": label,
        "tension_detail": t_detail,
        "complementarity_detail": c_detail,
        "volatility_detail": v_detail,
    }
