"""
Chained T/C/V Computation Engine — Plot Sim Core

Runs a sequence of scenario blocks against a party of characters,
computing how T/C/V scores shift at each node. Each block's output
state feeds the next block's input — relationships have memory.

Pure computation. No LLM calls. The narrative_seed field on ScenarioBlock
is metadata for downstream LLM generation — this module passes it through.
"""

from dataclasses import dataclass, field

from archetypes_core.engine.tcv import (
    compute_pair_scores,
    T_SCALE,
    C_SCALE,
    V_SCALE,
    V_UNTRIGGERED_DAMPEN,
)
from archetypes_core.engine.party import compute_party_matrix
from archetypes_core.engine.pressure import (
    TCVModifiers,
    compute_modifiers,
    apply_weight_amplifications,
)
from archetypes_core.scenarios.blocks import ScenarioBlock


# Critical moment detection threshold
CRITICAL_THRESHOLD = 0.15


@dataclass
class CriticalMoment:
    """A significant shift detected at a specific block."""
    block_id: str
    block_name: str
    moment_type: str  # "tension_spike", "shadow_trigger", "complementarity_breakthrough", "volatility_surge"
    pair_key: str
    char_a_name: str
    char_b_name: str
    magnitude: float
    description: str


@dataclass
class PairState:
    """Cumulative state for one character pair across the chain."""
    pair_key: str
    char_a_id: str
    char_b_id: str
    char_a_name: str
    char_b_name: str
    baseline_t: float
    baseline_c: float
    baseline_v: float
    t_history: list[float] = field(default_factory=list)
    c_history: list[float] = field(default_factory=list)
    v_history: list[float] = field(default_factory=list)
    label_history: list[str] = field(default_factory=list)
    critical_moments: list[CriticalMoment] = field(default_factory=list)

    @property
    def net_t_shift(self) -> float:
        return round(self.t_history[-1] - self.baseline_t, 3) if self.t_history else 0.0

    @property
    def net_c_shift(self) -> float:
        return round(self.c_history[-1] - self.baseline_c, 3) if self.c_history else 0.0

    @property
    def net_v_shift(self) -> float:
        return round(self.v_history[-1] - self.baseline_v, 3) if self.v_history else 0.0

    def to_dict(self) -> dict:
        return {
            "pair_key": self.pair_key,
            "char_a_id": self.char_a_id,
            "char_b_id": self.char_b_id,
            "char_a_name": self.char_a_name,
            "char_b_name": self.char_b_name,
            "baseline": {"t": self.baseline_t, "c": self.baseline_c, "v": self.baseline_v},
            "t_history": self.t_history,
            "c_history": self.c_history,
            "v_history": self.v_history,
            "label_history": self.label_history,
            "net_shift": {"t": self.net_t_shift, "c": self.net_c_shift, "v": self.net_v_shift},
            "critical_moments": [
                {
                    "block_id": cm.block_id,
                    "block_name": cm.block_name,
                    "moment_type": cm.moment_type,
                    "magnitude": cm.magnitude,
                    "description": cm.description,
                }
                for cm in self.critical_moments
            ],
        }


@dataclass
class BlockResult:
    """Results from one block in the chain."""
    block_id: str
    block_name: str
    situation_ids: list[str]
    modifiers: TCVModifiers
    pair_scores: list[dict]
    activated_shadows: list[dict]
    critical_moments: list[CriticalMoment]

    def to_dict(self) -> dict:
        return {
            "block_id": self.block_id,
            "block_name": self.block_name,
            "situation_ids": self.situation_ids,
            "modifiers_description": self.modifiers.describe(),
            "pair_scores": self.pair_scores,
            "activated_shadows": self.activated_shadows,
            "critical_moments": [
                {
                    "pair_key": cm.pair_key,
                    "moment_type": cm.moment_type,
                    "magnitude": cm.magnitude,
                    "description": cm.description,
                }
                for cm in self.critical_moments
            ],
        }


@dataclass
class ChainState:
    """Complete state of a plot simulation chain."""
    pair_states: dict[str, PairState]
    block_results: list[BlockResult]
    characters: list[dict]  # original characters (for reference)
    blocks: list[dict]  # original block definitions

    def to_dict(self) -> dict:
        return {
            "pair_states": {k: v.to_dict() for k, v in self.pair_states.items()},
            "block_results": [br.to_dict() for br in self.block_results],
            "block_count": len(self.block_results),
            "pair_count": len(self.pair_states),
        }


def _pair_key(char_a_id: str, char_b_id: str) -> str:
    """Canonical pair key (alphabetically ordered)."""
    return f"{min(char_a_id, char_b_id)}:{max(char_a_id, char_b_id)}"


def _detect_critical_moments(
    block: ScenarioBlock,
    current_scores: dict[str, dict],
    previous_scores: dict[str, dict],
    shadow_info: list[dict],
) -> list[CriticalMoment]:
    """Detect significant score shifts between consecutive blocks."""
    moments = []

    for pk, curr in current_scores.items():
        prev = previous_scores.get(pk)
        if not prev:
            continue

        dt = curr["t"] - prev["t"]
        dc = curr["c"] - prev["c"]
        dv = curr["v"] - prev["v"]

        if dt > CRITICAL_THRESHOLD:
            moments.append(CriticalMoment(
                block_id=block.block_id,
                block_name=block.name,
                moment_type="tension_spike",
                pair_key=pk,
                char_a_name=curr["a_name"],
                char_b_name=curr["b_name"],
                magnitude=round(dt, 3),
                description=f"Tension surged +{dt:.2f} between {curr['a_name']} and {curr['b_name']}",
            ))

        if dc > CRITICAL_THRESHOLD:
            moments.append(CriticalMoment(
                block_id=block.block_id,
                block_name=block.name,
                moment_type="complementarity_breakthrough",
                pair_key=pk,
                char_a_name=curr["a_name"],
                char_b_name=curr["b_name"],
                magnitude=round(dc, 3),
                description=f"Complementarity breakthrough +{dc:.2f} between {curr['a_name']} and {curr['b_name']}",
            ))

        if dv > CRITICAL_THRESHOLD:
            moments.append(CriticalMoment(
                block_id=block.block_id,
                block_name=block.name,
                moment_type="volatility_surge",
                pair_key=pk,
                char_a_name=curr["a_name"],
                char_b_name=curr["b_name"],
                magnitude=round(dv, 3),
                description=f"Volatility surged +{dv:.2f} between {curr['a_name']} and {curr['b_name']}",
            ))

    # Shadow triggers
    for shadow in shadow_info:
        moments.append(CriticalMoment(
            block_id=block.block_id,
            block_name=block.name,
            moment_type="shadow_trigger",
            pair_key=shadow.get("pair_key", ""),
            char_a_name=shadow.get("char_name", ""),
            char_b_name=shadow.get("triggered_by_name", ""),
            magnitude=shadow.get("contribution", 0.0),
            description=shadow.get("description", "Shadow primitive activated"),
        ))

    return moments


def _detect_shadow_activations(
    pair_scores: list[dict],
    previous_pair_scores: list[dict],
    shadow_boost: float,
) -> list[dict]:
    """Detect shadows that activated at this block but weren't active before."""
    activations = []

    for curr_pair in pair_scores:
        pk = _pair_key(curr_pair["a"], curr_pair["b"])

        # Find corresponding previous pair
        prev_pair = None
        for pp in previous_pair_scores:
            if _pair_key(pp["a"], pp["b"]) == pk:
                prev_pair = pp
                break

        if not prev_pair:
            continue

        # Check volatility details for newly triggered shadows
        prev_triggered = set()
        for vd in prev_pair.get("volatility_detail", []):
            if vd.get("triggered_by"):
                prev_triggered.add(vd["shadow_primitive"])

        for vd in curr_pair.get("volatility_detail", []):
            if vd.get("triggered_by") and vd["shadow_primitive"] not in prev_triggered:
                activations.append({
                    "pair_key": pk,
                    "shadow_primitive": vd["shadow_primitive"],
                    "triggered_by": vd["triggered_by"],
                    "contribution": vd["contribution"],
                    "char_name": curr_pair["a_name"] if vd["source"] == "a_shadow" else curr_pair["b_name"],
                    "triggered_by_name": curr_pair["b_name"] if vd["source"] == "a_shadow" else curr_pair["a_name"],
                    "description": f"{vd['shadow_primitive']} shadow activated in {'A' if vd['source'] == 'a_shadow' else 'B'}",
                })

    return activations


def run_chain(
    characters: list[dict],
    blocks: list[ScenarioBlock],
    *,
    t_scale: float = T_SCALE,
    c_scale: float = C_SCALE,
    v_scale: float = V_SCALE,
    v_dampen: float = V_UNTRIGGERED_DAMPEN,
) -> ChainState:
    """
    Run a sequence of scenario blocks against a party of characters.

    Each block:
    1. Computes T/C/V modifiers from its situation primitives
    2. Applies weight amplifications to character primitives (temporary copy)
    3. Runs compute_party_matrix with modified scales
    4. Detects critical moments (score jumps, shadow activations)
    5. Updates cumulative pair states

    Characters accumulate state across blocks. A shadow triggered in block 2
    stays relevant for blocks 3+. Order matters because relationships have memory.

    Returns a ChainState with per-pair histories and per-block results.
    """
    if not characters or not blocks:
        return ChainState(
            pair_states={},
            block_results=[],
            characters=characters,
            blocks=[b.to_dict() for b in blocks],
        )

    # Compute baseline (no situation pressure)
    baseline = compute_party_matrix(characters, t_scale=t_scale, c_scale=c_scale,
                                     v_scale=v_scale, v_dampen=v_dampen)

    # Initialize pair states from baseline
    pair_states: dict[str, PairState] = {}
    baseline_scores: dict[str, dict] = {}
    for pair in baseline["pairs"]:
        pk = _pair_key(pair["a"], pair["b"])
        pair_states[pk] = PairState(
            pair_key=pk,
            char_a_id=pair["a"],
            char_b_id=pair["b"],
            char_a_name=pair["a_name"],
            char_b_name=pair["b_name"],
            baseline_t=pair["t"],
            baseline_c=pair["c"],
            baseline_v=pair["v"],
        )
        baseline_scores[pk] = pair

    # Track previous block's scores for delta detection
    previous_scores = baseline_scores
    previous_pair_list = baseline["pairs"]
    block_results: list[BlockResult] = []

    # Cumulative shadow state: once a shadow triggers, it stays triggered
    # We track this by gradually reducing the dampen factor for triggered shadows
    cumulative_shadow_boost = 0.0

    for block in blocks:
        # 1. Compute modifiers from situation primitives
        modifiers = compute_modifiers(block.situation_ids)

        # Add cumulative shadow boost from previous blocks
        effective_shadow_boost = modifiers.shadow_trigger_boost + cumulative_shadow_boost

        # 2. Apply weight amplifications to characters (temporary copies)
        if modifiers.weight_amplifications:
            modified_chars = apply_weight_amplifications(characters, modifiers.weight_amplifications)
        else:
            modified_chars = characters

        # 3. Compute party matrix with modified scales
        effective_t = t_scale * modifiers.t_scale_modifier
        effective_c = c_scale * modifiers.c_scale_modifier
        effective_v = v_scale * modifiers.v_scale_modifier
        # Shadow boost reduces the dampen factor (making untriggered shadows more active)
        effective_dampen = max(0.05, v_dampen - effective_shadow_boost)

        result = compute_party_matrix(
            modified_chars,
            t_scale=effective_t,
            c_scale=effective_c,
            v_scale=effective_v,
            v_dampen=effective_dampen,
        )

        # 4. Build current scores lookup and detect changes
        current_scores: dict[str, dict] = {}
        for pair in result["pairs"]:
            pk = _pair_key(pair["a"], pair["b"])
            current_scores[pk] = pair

        # Detect shadow activations
        activated_shadows = _detect_shadow_activations(
            result["pairs"], previous_pair_list, effective_shadow_boost
        )

        # Detect critical moments
        critical_moments = _detect_critical_moments(
            block, current_scores, previous_scores, activated_shadows
        )

        # 5. Update pair states
        for pk, ps in pair_states.items():
            curr = current_scores.get(pk)
            if curr:
                ps.t_history.append(curr["t"])
                ps.c_history.append(curr["c"])
                ps.v_history.append(curr["v"])
                ps.label_history.append(curr["label"]["label"])
                # Add critical moments for this pair
                for cm in critical_moments:
                    if cm.pair_key == pk:
                        ps.critical_moments.append(cm)

        # Accumulate shadow boost for future blocks
        if activated_shadows:
            cumulative_shadow_boost += 0.02 * len(activated_shadows)

        # Record block result
        block_results.append(BlockResult(
            block_id=block.block_id,
            block_name=block.name,
            situation_ids=block.situation_ids,
            modifiers=modifiers,
            pair_scores=result["pairs"],
            activated_shadows=activated_shadows,
            critical_moments=critical_moments,
        ))

        # Update previous state for next iteration
        previous_scores = current_scores
        previous_pair_list = result["pairs"]

    return ChainState(
        pair_states=pair_states,
        block_results=block_results,
        characters=characters,
        blocks=[b.to_dict() for b in blocks],
    )
