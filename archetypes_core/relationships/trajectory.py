"""
Relationship Trajectory Classification

Classifies how a pair's relationship evolves across a plot simulation chain.
Operates on PairState output from the chain engine.

Pure computation. No LLM calls.
"""

from dataclasses import dataclass

from archetypes_core.engine.chain import PairState, ChainState, CriticalMoment
from archetypes_core.engine.party import classify_pair


@dataclass
class TrajectoryArc:
    """Classification of a pair's journey through the chain."""
    arc_type: str       # "deepening", "fracturing", "oscillating", "stable", "transforming"
    description: str
    confidence: float   # 0-1, how clearly the data supports this classification
    key_moments: list[CriticalMoment]
    before_tcv: tuple[float, float, float]
    after_tcv: tuple[float, float, float]
    net_shift: tuple[float, float, float]

    def to_dict(self) -> dict:
        return {
            "arc_type": self.arc_type,
            "description": self.description,
            "confidence": self.confidence,
            "key_moments": [
                {
                    "block_name": cm.block_name,
                    "moment_type": cm.moment_type,
                    "magnitude": cm.magnitude,
                    "description": cm.description,
                }
                for cm in self.key_moments
            ],
            "before_tcv": {"t": self.before_tcv[0], "c": self.before_tcv[1], "v": self.before_tcv[2]},
            "after_tcv": {"t": self.after_tcv[0], "c": self.after_tcv[1], "v": self.after_tcv[2]},
            "net_shift": {"t": self.net_shift[0], "c": self.net_shift[1], "v": self.net_shift[2]},
        }


@dataclass
class ChainSummary:
    """Summary of an entire plot simulation chain."""
    pair_trajectories: dict[str, TrajectoryArc]
    critical_block: str       # block_id with max aggregate delta
    critical_pair: str        # pair_key with largest net shift
    party_trajectory: str     # overall party arc description

    def to_dict(self) -> dict:
        return {
            "pair_trajectories": {k: v.to_dict() for k, v in self.pair_trajectories.items()},
            "critical_block": self.critical_block,
            "critical_pair": self.critical_pair,
            "party_trajectory": self.party_trajectory,
        }


def _is_monotonic_increasing(values: list[float], tolerance: float = 0.02) -> bool:
    """Check if values trend upward (allowing small dips)."""
    if len(values) < 2:
        return False
    increases = sum(1 for i in range(1, len(values)) if values[i] > values[i - 1] - tolerance)
    return increases >= len(values) * 0.6


def _is_monotonic_decreasing(values: list[float], tolerance: float = 0.02) -> bool:
    """Check if values trend downward (allowing small bumps)."""
    if len(values) < 2:
        return False
    decreases = sum(1 for i in range(1, len(values)) if values[i] < values[i - 1] + tolerance)
    return decreases >= len(values) * 0.6


def _max_swing(values: list[float]) -> float:
    """Maximum consecutive delta in a series."""
    if len(values) < 2:
        return 0.0
    return max(abs(values[i] - values[i - 1]) for i in range(1, len(values)))


def classify_trajectory(pair_state: PairState) -> TrajectoryArc:
    """
    Classify the overall arc of a relationship across the chain.

    Classification rules (pure math):
    - Deepening: C increases or net C shift > +0.15, T stable or decreasing
    - Fracturing: T increases while C decreases, or net T shift > +0.15 with V rising
    - Oscillating: T or C swing > 0.12 between consecutive blocks, no monotonic trend
    - Stable: all per-block deltas < 0.05
    - Transforming: pair label changes between first and last block
    """
    t_hist = pair_state.t_history
    c_hist = pair_state.c_history
    v_hist = pair_state.v_history
    labels = pair_state.label_history

    before = (pair_state.baseline_t, pair_state.baseline_c, pair_state.baseline_v)
    after = (t_hist[-1], c_hist[-1], v_hist[-1]) if t_hist else before
    net = (pair_state.net_t_shift, pair_state.net_c_shift, pair_state.net_v_shift)

    if not t_hist:
        return TrajectoryArc(
            arc_type="stable",
            description="No blocks processed — relationship unchanged.",
            confidence=1.0,
            key_moments=[],
            before_tcv=before,
            after_tcv=after,
            net_shift=net,
        )

    # Check for label transformation
    label_changed = labels[0] != labels[-1] if labels else False

    # Compute metrics
    t_swing = _max_swing(t_hist)
    c_swing = _max_swing(c_hist)
    net_t = pair_state.net_t_shift
    net_c = pair_state.net_c_shift
    net_v = pair_state.net_v_shift
    all_deltas_small = all(
        abs(t_hist[i] - t_hist[i - 1]) < 0.05 and
        abs(c_hist[i] - c_hist[i - 1]) < 0.05 and
        abs(v_hist[i] - v_hist[i - 1]) < 0.05
        for i in range(1, len(t_hist))
    ) if len(t_hist) > 1 else True

    # Classification with confidence scoring
    # Check stable first (easiest to confirm)
    if all_deltas_small and abs(net_t) < 0.05 and abs(net_c) < 0.05 and abs(net_v) < 0.05:
        return TrajectoryArc(
            arc_type="stable",
            description=f"{pair_state.char_a_name} and {pair_state.char_b_name}'s relationship held steady throughout — neither pressure nor opportunity shifted their dynamic.",
            confidence=0.9,
            key_moments=pair_state.critical_moments,
            before_tcv=before,
            after_tcv=after,
            net_shift=net,
        )

    # Check transforming (label change is the clearest signal)
    if label_changed:
        return TrajectoryArc(
            arc_type="transforming",
            description=f"{pair_state.char_a_name} and {pair_state.char_b_name} transformed from '{labels[0]}' to '{labels[-1]}' — a fundamental shift in their dynamic.",
            confidence=0.85,
            key_moments=pair_state.critical_moments,
            before_tcv=before,
            after_tcv=after,
            net_shift=net,
        )

    # Check oscillating (high swings without clear trend)
    if (t_swing > 0.12 or c_swing > 0.12) and not _is_monotonic_increasing(t_hist) and not _is_monotonic_decreasing(t_hist):
        return TrajectoryArc(
            arc_type="oscillating",
            description=f"{pair_state.char_a_name} and {pair_state.char_b_name} oscillated — their relationship swung between states without settling.",
            confidence=0.7,
            key_moments=pair_state.critical_moments,
            before_tcv=before,
            after_tcv=after,
            net_shift=net,
        )

    # Check deepening (C rising, T stable or falling)
    if net_c > 0.10 and net_t <= 0.05:
        confidence = min(0.9, 0.5 + abs(net_c))
        return TrajectoryArc(
            arc_type="deepening",
            description=f"{pair_state.char_a_name} and {pair_state.char_b_name} deepened their bond — complementarity grew as pressures revealed shared ground.",
            confidence=confidence,
            key_moments=pair_state.critical_moments,
            before_tcv=before,
            after_tcv=after,
            net_shift=net,
        )

    # Check fracturing (T rising, C falling or V rising)
    if net_t > 0.10 and (net_c < -0.05 or net_v > 0.05):
        confidence = min(0.9, 0.5 + abs(net_t))
        return TrajectoryArc(
            arc_type="fracturing",
            description=f"{pair_state.char_a_name} and {pair_state.char_b_name} fractured under pressure — tension grew while their connection eroded.",
            confidence=confidence,
            key_moments=pair_state.critical_moments,
            before_tcv=before,
            after_tcv=after,
            net_shift=net,
        )

    # Default: classify by dominant shift direction
    dominant_shift = max(abs(net_t), abs(net_c), abs(net_v))
    if abs(net_c) == dominant_shift and net_c > 0:
        arc_type = "deepening"
        desc = f"{pair_state.char_a_name} and {pair_state.char_b_name} gradually deepened their connection through shared pressure."
    elif abs(net_t) == dominant_shift and net_t > 0:
        arc_type = "fracturing"
        desc = f"{pair_state.char_a_name} and {pair_state.char_b_name} drifted apart as tension accumulated."
    else:
        arc_type = "stable"
        desc = f"{pair_state.char_a_name} and {pair_state.char_b_name}'s relationship shifted subtly but maintained its essential character."

    return TrajectoryArc(
        arc_type=arc_type,
        description=desc,
        confidence=0.5,
        key_moments=pair_state.critical_moments,
        before_tcv=before,
        after_tcv=after,
        net_shift=net,
    )


def summarize_chain(chain_state: ChainState) -> ChainSummary:
    """
    Compute trajectory arcs for all pairs, identify critical block and pair.

    Returns a ChainSummary with:
    - Per-pair trajectory classifications
    - The block that caused the biggest aggregate shift
    - The pair with the largest net shift
    - An overall party trajectory description
    """
    # Classify each pair's trajectory
    pair_trajectories: dict[str, TrajectoryArc] = {}
    for pk, ps in chain_state.pair_states.items():
        pair_trajectories[pk] = classify_trajectory(ps)

    # Find critical block (max aggregate delta)
    critical_block = ""
    max_block_delta = 0.0
    for i, br in enumerate(chain_state.block_results):
        block_delta = sum(cm.magnitude for cm in br.critical_moments)
        if block_delta > max_block_delta:
            max_block_delta = block_delta
            critical_block = br.block_id

    # Find critical pair (largest total net shift)
    critical_pair = ""
    max_pair_shift = 0.0
    for pk, ps in chain_state.pair_states.items():
        total_shift = abs(ps.net_t_shift) + abs(ps.net_c_shift) + abs(ps.net_v_shift)
        if total_shift > max_pair_shift:
            max_pair_shift = total_shift
            critical_pair = pk

    # Compute overall party trajectory
    arc_counts: dict[str, int] = {}
    for traj in pair_trajectories.values():
        arc_counts[traj.arc_type] = arc_counts.get(traj.arc_type, 0) + 1

    dominant_arc = max(arc_counts, key=arc_counts.get) if arc_counts else "stable"
    total_pairs = len(pair_trajectories)

    if dominant_arc == "stable" and arc_counts.get("stable", 0) == total_pairs:
        party_trajectory = "The party weathered all pressures without significant relationship shifts."
    elif dominant_arc == "deepening":
        party_trajectory = "The party emerged closer — shared pressures forged stronger bonds across multiple pairs."
    elif dominant_arc == "fracturing":
        party_trajectory = "The pressures took their toll — the party's internal tensions widened into fractures."
    elif dominant_arc == "transforming":
        party_trajectory = "The party was fundamentally transformed — key relationships changed their essential character."
    elif dominant_arc == "oscillating":
        party_trajectory = "The party's relationships swung wildly — pressures created instability without resolution."
    else:
        party_trajectory = "The party experienced a mix of deepening, fracturing, and shifting dynamics."

    return ChainSummary(
        pair_trajectories=pair_trajectories,
        critical_block=critical_block,
        critical_pair=critical_pair,
        party_trajectory=party_trajectory,
    )
