"""
Archetypal Intelligence — Drift Analysis

Pure computation on decomposed lineage variants. No LLM calls.

Three layers of analysis:
  1. Pairwise drift  — what changed between two variants
  2. Core extraction — what persists across ALL variants (the irreducible archetype)
  3. Tradition fingerprint — what a tradition consistently does to archetypes passing through it
"""

from archetypes_core.drift.lineage import Lineage, Variant
from archetypes_core.primitives import PRIMITIVES, CATEGORIES


# ---------------------------------------------------------------------------
# 1. Pairwise Drift
# ---------------------------------------------------------------------------

def compute_drift(variant_a: Variant, variant_b: Variant) -> dict:
    """
    Compare two variants of the same archetype. Returns:
      - gained: primitives present in B but absent in A
      - lost: primitives present in A but absent in B
      - amplified: primitives whose weight increased (A->B)
      - suppressed: primitives whose weight decreased (A->B)
      - stable: primitives with similar weight in both (delta < threshold)
      - shadow_drift: changes in shadow composition
      - total_drift: scalar measure of how much changed (0 = identical, 1 = completely different)
    """
    wa = variant_a.primitive_weights()
    wb = variant_b.primitive_weights()
    all_prims = set(wa.keys()) | set(wb.keys())

    gained = []
    lost = []
    amplified = []
    suppressed = []
    stable = []
    THRESHOLD = 0.05  # Below this delta, consider stable

    for pid in all_prims:
        a_w = wa.get(pid, 0.0)
        b_w = wb.get(pid, 0.0)
        delta = b_w - a_w
        prim_name = PRIMITIVES.get(pid, {}).get("name", pid)
        category = PRIMITIVES.get(pid, {}).get("category", "unknown")

        entry = {
            "primitive_id": pid,
            "name": prim_name,
            "category": category,
            "weight_a": round(a_w, 3),
            "weight_b": round(b_w, 3),
            "delta": round(delta, 3),
        }

        if a_w == 0.0 and b_w > 0.0:
            gained.append(entry)
        elif a_w > 0.0 and b_w == 0.0:
            lost.append(entry)
        elif abs(delta) < THRESHOLD:
            stable.append(entry)
        elif delta > 0:
            amplified.append(entry)
        else:
            suppressed.append(entry)

    # Shadow drift
    sa = variant_a.shadow_weights()
    sb = variant_b.shadow_weights()
    shadow_gained = [
        {"primitive_id": pid, "name": PRIMITIVES.get(pid, {}).get("name", pid), "weight": round(sb[pid], 3)}
        for pid in sb if pid not in sa
    ]
    shadow_lost = [
        {"primitive_id": pid, "name": PRIMITIVES.get(pid, {}).get("name", pid), "weight": round(sa[pid], 3)}
        for pid in sa if pid not in sb
    ]

    # Total drift: sum of absolute deltas across all primitives (normalized)
    total_delta = sum(abs(wb.get(p, 0.0) - wa.get(p, 0.0)) for p in all_prims)
    # Max possible drift is 2.0 (one set sums to 1.0, completely disjoint from the other)
    total_drift = round(min(total_delta / 2.0, 1.0), 3)

    return {
        "from": {"id": variant_a.id, "name": variant_a.name, "tradition": variant_a.tradition, "era": variant_a.era},
        "to": {"id": variant_b.id, "name": variant_b.name, "tradition": variant_b.tradition, "era": variant_b.era},
        "gained": sorted(gained, key=lambda x: x["weight_b"], reverse=True),
        "lost": sorted(lost, key=lambda x: x["weight_a"], reverse=True),
        "amplified": sorted(amplified, key=lambda x: x["delta"], reverse=True),
        "suppressed": sorted(suppressed, key=lambda x: x["delta"]),
        "stable": stable,
        "shadow_drift": {"gained": shadow_gained, "lost": shadow_lost},
        "total_drift": total_drift,
    }


def compute_full_trajectory(lineage: Lineage) -> list[dict]:
    """
    Compute sequential drift across all variants in chronological order.
    Returns a list of drift dicts: [A->B, B->C, C->D, ...].
    """
    variants = lineage.chronological()
    trajectory = []
    for i in range(len(variants) - 1):
        trajectory.append(compute_drift(variants[i], variants[i + 1]))
    return trajectory


# ---------------------------------------------------------------------------
# 2. Core Extraction
# ---------------------------------------------------------------------------

def extract_core(lineage: Lineage, presence_threshold: float = 0.10) -> dict:
    """
    Find primitives present in ALL variants above a weight threshold.
    These are the archetype's irreducible essence — what survives
    every tradition's transformation.

    Returns:
      - core: list of {primitive_id, name, min_weight, max_weight, mean_weight}
      - periphery: primitives that appear in some but not all variants
      - core_stability: ratio of core weight to total (higher = more resistant to transformation)
    """
    variants = lineage.chronological()
    if not variants:
        return {"core": [], "periphery": [], "core_stability": 0.0}

    # Collect all primitive IDs that appear in any variant
    all_prims = set()
    for v in variants:
        all_prims.update(v.primitive_weights().keys())

    core = []
    periphery = []

    for pid in all_prims:
        weights = []
        for v in variants:
            w = v.primitive_weights().get(pid, 0.0)
            weights.append(w)

        present_in_all = all(w >= presence_threshold for w in weights)
        prim_name = PRIMITIVES.get(pid, {}).get("name", pid)
        category = PRIMITIVES.get(pid, {}).get("category", "unknown")

        entry = {
            "primitive_id": pid,
            "name": prim_name,
            "category": category,
            "weights_by_variant": {v.id: round(v.primitive_weights().get(pid, 0.0), 3) for v in variants},
            "min_weight": round(min(weights), 3),
            "max_weight": round(max(weights), 3),
            "mean_weight": round(sum(weights) / len(weights), 3),
            "weight_range": round(max(weights) - min(weights), 3),
        }

        if present_in_all:
            core.append(entry)
        else:
            entry["appearances"] = sum(1 for w in weights if w >= presence_threshold)
            entry["total_variants"] = len(variants)
            periphery.append(entry)

    core.sort(key=lambda x: x["mean_weight"], reverse=True)
    periphery.sort(key=lambda x: x["appearances"], reverse=True)

    # Core stability: what fraction of average weight is in core primitives
    total_core_weight = sum(p["mean_weight"] for p in core)
    core_stability = round(total_core_weight, 3)  # Weights sum to 1.0, so this is the fraction

    return {
        "core": core,
        "periphery": periphery,
        "core_stability": core_stability,
        "variant_count": len(variants),
    }


# ---------------------------------------------------------------------------
# 3. Tradition Fingerprint
# ---------------------------------------------------------------------------

def tradition_fingerprint(lineages: list[Lineage], tradition: str) -> dict:
    """
    Aggregate what a tradition does to archetypes passing through it.
    Requires multiple lineages with variants in the same tradition.

    For each lineage that has a variant in this tradition AND at least one
    variant in a different tradition, compute what the tradition added/amplified
    vs. removed/suppressed. Aggregate across lineages.

    Returns:
      - amplifies: primitives this tradition consistently strengthens
      - suppresses: primitives this tradition consistently weakens
      - introduces: primitives this tradition adds that weren't there before
      - removes: primitives this tradition drops
      - sample_size: how many lineages contributed to this fingerprint
    """
    # Track net effects across lineages
    effects: dict[str, list[float]] = {}  # primitive_id -> list of deltas

    sample_count = 0
    for lineage in lineages:
        tradition_variants = [v for v in lineage.variants if v.tradition == tradition]
        other_variants = [v for v in lineage.variants if v.tradition != tradition]

        if not tradition_variants or not other_variants:
            continue

        sample_count += 1

        # Average the tradition variant weights and compare to average of others
        t_weights: dict[str, float] = {}
        for v in tradition_variants:
            for pid, w in v.primitive_weights().items():
                t_weights[pid] = t_weights.get(pid, 0.0) + w
        for pid in t_weights:
            t_weights[pid] /= len(tradition_variants)

        o_weights: dict[str, float] = {}
        for v in other_variants:
            for pid, w in v.primitive_weights().items():
                o_weights[pid] = o_weights.get(pid, 0.0) + w
        for pid in o_weights:
            o_weights[pid] /= len(other_variants)

        all_prims = set(t_weights.keys()) | set(o_weights.keys())
        for pid in all_prims:
            delta = t_weights.get(pid, 0.0) - o_weights.get(pid, 0.0)
            if pid not in effects:
                effects[pid] = []
            effects[pid].append(delta)

    if sample_count == 0:
        return {"amplifies": [], "suppresses": [], "introduces": [], "removes": [], "sample_size": 0}

    amplifies = []
    suppresses = []
    introduces = []
    removes = []
    THRESHOLD = 0.03

    for pid, deltas in effects.items():
        mean_delta = sum(deltas) / len(deltas)
        prim_name = PRIMITIVES.get(pid, {}).get("name", pid)
        category = PRIMITIVES.get(pid, {}).get("category", "unknown")

        entry = {
            "primitive_id": pid,
            "name": prim_name,
            "category": category,
            "mean_delta": round(mean_delta, 3),
            "consistency": round(sum(1 for d in deltas if (d > 0) == (mean_delta > 0)) / len(deltas), 2),
        }

        avg_other = sum(max(0, -d + mean_delta) for d in deltas) / len(deltas)
        if mean_delta > THRESHOLD:
            if avg_other < THRESHOLD:
                introduces.append(entry)
            else:
                amplifies.append(entry)
        elif mean_delta < -THRESHOLD:
            removes.append(entry)

    amplifies.sort(key=lambda x: x["mean_delta"], reverse=True)
    suppresses.sort(key=lambda x: x["mean_delta"])
    introduces.sort(key=lambda x: x["mean_delta"], reverse=True)
    removes.sort(key=lambda x: x["mean_delta"])

    return {
        "tradition": tradition,
        "amplifies": amplifies,
        "suppresses": suppresses,
        "introduces": introduces,
        "removes": removes,
        "sample_size": sample_count,
    }


# ---------------------------------------------------------------------------
# 4. Category Shift Analysis
# ---------------------------------------------------------------------------

def category_shift(variant_a: Variant, variant_b: Variant) -> dict:
    """
    Show how weight distribution across categories changes between variants.
    Reveals high-level shifts like "from behavioral to emotional" or
    "from values to cognitive."
    """
    def _cat_weights(variant: Variant) -> dict[str, float]:
        totals: dict[str, float] = {cat: 0.0 for cat in CATEGORIES}
        for p in variant.primary:
            cat = PRIMITIVES.get(p["primitive_id"], {}).get("category", "unknown")
            if cat in totals:
                totals[cat] += p["weight"]
        return totals

    ca = _cat_weights(variant_a)
    cb = _cat_weights(variant_b)

    shifts = []
    for cat in CATEGORIES:
        delta = cb.get(cat, 0.0) - ca.get(cat, 0.0)
        shifts.append({
            "category": cat,
            "category_name": CATEGORIES[cat]["name"],
            "weight_a": round(ca.get(cat, 0.0), 3),
            "weight_b": round(cb.get(cat, 0.0), 3),
            "delta": round(delta, 3),
        })

    shifts.sort(key=lambda x: abs(x["delta"]), reverse=True)
    return {
        "from": variant_a.name,
        "to": variant_b.name,
        "shifts": shifts,
    }


# ---------------------------------------------------------------------------
# 5. Full Lineage Report
# ---------------------------------------------------------------------------

def full_lineage_report(lineage: Lineage) -> dict:
    """
    Complete analysis of a lineage: trajectory, core, category shifts,
    and per-variant summaries. This is the main entry point for the UI.
    """
    variants = lineage.chronological()
    trajectory = compute_full_trajectory(lineage)
    core = extract_core(lineage)
    cat_shifts = []
    for i in range(len(variants) - 1):
        cat_shifts.append(category_shift(variants[i], variants[i + 1]))

    return {
        "lineage_id": lineage.id,
        "lineage_name": lineage.name,
        "description": lineage.description,
        "variant_count": len(variants),
        "variants": [
            {
                "id": v.id,
                "name": v.name,
                "tradition": v.tradition,
                "era": v.era,
                "source_work": v.source_work,
                "primary_count": len(v.primary),
                "shadow_count": len(v.shadow),
            }
            for v in variants
        ],
        "trajectory": trajectory,
        "core": core,
        "category_shifts": cat_shifts,
    }
