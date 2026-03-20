"""
Archetypal Intelligence — Party Analysis

Computes all pairwise T/C/V scores for a party of characters,
aggregates, highlights, and qualitative pair classification.
"""

from archetypes_core.engine.tcv import (
    compute_pair_scores,
    T_SCALE,
    C_SCALE,
    V_SCALE,
    V_UNTRIGGERED_DAMPEN,
)


def classify_pair(t: float, c: float, v: float) -> dict:
    """
    Returns a qualitative label and description for a pair based on T/C/V.
    Thresholds: low < 0.3, mid 0.3–0.6, high > 0.6.
    """
    high_t = t > 0.5
    high_c = c > 0.5
    high_v = v > 0.5

    if high_v:
        return {
            "label": "Unpredictable",
            "description": "Shadow dynamics dominate — depends entirely on triggers",
            "icon": "lightning",
        }
    if high_t and high_c:
        return {
            "label": "Explosive but rewarding",
            "description": "Deep friction AND deep synergy — the richest roleplay ground",
            "icon": "fire",
        }
    if high_t and not high_c:
        return {
            "label": "Straight conflict",
            "description": "Fundamental opposition with little to bridge the gap",
            "icon": "swords",
        }
    if not high_t and high_c:
        return {
            "label": "Reliable partnership",
            "description": "Strong mutual support, covers each other's gaps",
            "icon": "handshake",
        }
    if t > 0.3 and c > 0.3:
        return {
            "label": "Interesting tension",
            "description": "Enough friction to spark, enough synergy to sustain",
            "icon": "spark",
        }
    if t > 0.3:
        return {
            "label": "Simmering friction",
            "description": "Underlying disagreement that could escalate",
            "icon": "heat",
        }
    if c > 0.3:
        return {
            "label": "Quiet synergy",
            "description": "Complementary strengths without much dramatic charge",
            "icon": "link",
        }
    return {
        "label": "Little dynamic charge",
        "description": "Neutral — their primitives rarely interact",
        "icon": "neutral",
    }


def compute_party_matrix(characters: list[dict], *, t_scale=None, c_scale=None, v_scale=None, v_dampen=None) -> dict:
    """
    Given a list of characters, compute all pairwise T/C/V scores.

    Returns:
      pairs: list of pair score dicts
      aggregates: mean T, C, V across all pairs
      highlights: most explosive, most synergistic, most volatile pairs
      tuning: active scale values used for this computation
    """
    n = len(characters)
    pairs = []

    for i in range(n):
        for j in range(i + 1, n):
            pair = compute_pair_scores(characters[i], characters[j],
                                       t_scale=t_scale, c_scale=c_scale,
                                       v_scale=v_scale, v_dampen=v_dampen)
            pairs.append(pair)

    if not pairs:
        return {"pairs": [], "aggregates": {}, "highlights": {}}

    mean_t = round(sum(p["t"] for p in pairs) / len(pairs), 3)
    mean_c = round(sum(p["c"] for p in pairs) / len(pairs), 3)
    mean_v = round(sum(p["v"] for p in pairs) / len(pairs), 3)

    # Find highlights
    most_explosive = max(pairs, key=lambda p: p["t"] + p["c"])
    most_synergistic = max(pairs, key=lambda p: p["c"])
    most_volatile = max(pairs, key=lambda p: p["v"])
    most_charged = max(pairs, key=lambda p: p["t"] + p["c"] + p["v"])

    return {
        "pairs": pairs,
        "aggregates": {
            "mean_t": mean_t,
            "mean_c": mean_c,
            "mean_v": mean_v,
            "party_charge": round((mean_t + mean_c + mean_v) / 3, 3),
        },
        "highlights": {
            "most_explosive": {
                "pair": f"{most_explosive['a_name']} + {most_explosive['b_name']}",
                "t": most_explosive["t"],
                "c": most_explosive["c"],
            },
            "most_synergistic": {
                "pair": f"{most_synergistic['a_name']} + {most_synergistic['b_name']}",
                "c": most_synergistic["c"],
            },
            "most_volatile": {
                "pair": f"{most_volatile['a_name']} + {most_volatile['b_name']}",
                "v": most_volatile["v"],
            },
            "most_charged": {
                "pair": f"{most_charged['a_name']} + {most_charged['b_name']}",
                "total": round(most_charged["t"] + most_charged["c"] + most_charged["v"], 3),
            },
        },
        "tuning": {
            "t_scale": t_scale or T_SCALE,
            "c_scale": c_scale or C_SCALE,
            "v_scale": v_scale or V_SCALE,
            "v_dampen": v_dampen or V_UNTRIGGERED_DAMPEN,
        },
    }
