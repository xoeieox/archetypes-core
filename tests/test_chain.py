"""Chain engine and trajectory tracker tests."""

import sys
import pytest

sys.path.insert(0, "/data/kyma")

from archetypes_core.engine.chain import run_chain, ChainState, PairState
from archetypes_core.engine.pressure import compute_modifiers, apply_weight_amplifications, TCVModifiers
from archetypes_core.scenarios import SCENARIO_BLOCKS, ScenarioBlock
from archetypes_core.relationships import classify_trajectory, summarize_chain, TrajectoryArc


@pytest.fixture
def two_characters():
    return [
        {
            "id": "char-a",
            "name": "Warrior",
            "primary": [
                {"primitive_id": "duty-over-desire", "weight": 0.4},
                {"primitive_id": "justice-seeking", "weight": 0.35},
                {"primitive_id": "risk-taking", "weight": 0.25},
            ],
            "shadow": [{"primitive_id": "wrath", "weight": 0.15}],
        },
        {
            "id": "char-b",
            "name": "Trickster",
            "primary": [
                {"primitive_id": "strategic-deception", "weight": 0.4},
                {"primitive_id": "adaptive-flexibility", "weight": 0.35},
                {"primitive_id": "lateral-thinking", "weight": 0.25},
            ],
            "shadow": [{"primitive_id": "envy", "weight": 0.10}],
        },
    ]


class TestPressureComputation:
    def test_no_situations_returns_neutral_modifiers(self):
        mods = compute_modifiers([])
        assert mods.t_scale_modifier == 1.0
        assert mods.c_scale_modifier == 1.0
        assert mods.v_scale_modifier == 1.0
        assert mods.shadow_trigger_boost == 0.0

    def test_moderate_situation_increases_scales(self):
        mods = compute_modifiers(["resource-scarcity"])  # moderate intensity
        assert mods.t_scale_modifier > 1.0
        assert mods.v_scale_modifier > 1.0

    def test_extreme_situation_has_larger_effect(self):
        mod_moderate = compute_modifiers(["resource-scarcity"])  # moderate
        mod_extreme = compute_modifiers(["betrayal-discovery"])  # extreme
        assert mod_extreme.t_scale_modifier > mod_moderate.t_scale_modifier

    def test_multiple_situations_compound(self):
        mod_single = compute_modifiers(["resource-scarcity"])
        mod_double = compute_modifiers(["resource-scarcity", "power-imbalance"])
        assert mod_double.t_scale_modifier > mod_single.t_scale_modifier

    def test_weight_amplifications_created(self):
        mods = compute_modifiers(["resource-scarcity"])
        # resource-scarcity targets generosity, justice-seeking, etc.
        assert len(mods.weight_amplifications) > 0

    def test_apply_weight_amplifications_preserves_sum(self, two_characters):
        amps = {"duty-over-desire": 2.0, "strategic-deception": 0.5}
        modified = apply_weight_amplifications(two_characters, amps)
        for char in modified:
            total = sum(p["weight"] for p in char["primary"])
            assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, expected ~1.0"

    def test_apply_weight_amplifications_does_not_mutate_original(self, two_characters):
        original_weight = two_characters[0]["primary"][0]["weight"]
        amps = {"duty-over-desire": 2.0}
        _ = apply_weight_amplifications(two_characters, amps)
        assert two_characters[0]["primary"][0]["weight"] == original_weight


class TestChainEngine:
    def test_empty_characters(self):
        state = run_chain([], [SCENARIO_BLOCKS["betrayal-revealed"]])
        assert len(state.pair_states) == 0
        assert len(state.block_results) == 0

    def test_empty_blocks(self, two_characters):
        state = run_chain(two_characters, [])
        assert len(state.pair_states) == 0
        assert len(state.block_results) == 0

    def test_single_block(self, two_characters):
        state = run_chain(two_characters, [SCENARIO_BLOCKS["betrayal-revealed"]])
        assert len(state.block_results) == 1
        assert len(state.pair_states) == 1
        pk = list(state.pair_states.keys())[0]
        assert len(state.pair_states[pk].t_history) == 1

    def test_three_blocks_produce_three_history_entries(self, two_characters):
        blocks = [
            SCENARIO_BLOCKS["betrayal-revealed"],
            SCENARIO_BLOCKS["resources-run-dry"],
            SCENARIO_BLOCKS["moral-crossroads"],
        ]
        state = run_chain(two_characters, blocks)
        assert len(state.block_results) == 3
        for ps in state.pair_states.values():
            assert len(ps.t_history) == 3
            assert len(ps.c_history) == 3
            assert len(ps.v_history) == 3

    def test_scores_bounded(self, two_characters):
        blocks = [SCENARIO_BLOCKS[b] for b in ["betrayal-revealed", "resources-run-dry", "moral-crossroads"]]
        state = run_chain(two_characters, blocks)
        for ps in state.pair_states.values():
            for t in ps.t_history:
                assert 0.0 <= t <= 1.0
            for c in ps.c_history:
                assert 0.0 <= c <= 1.0
            for v in ps.v_history:
                assert 0.0 <= v <= 1.0

    def test_order_sensitivity(self, two_characters):
        blocks_abc = [
            SCENARIO_BLOCKS["betrayal-revealed"],
            SCENARIO_BLOCKS["resources-run-dry"],
            SCENARIO_BLOCKS["moral-crossroads"],
        ]
        blocks_cba = list(reversed(blocks_abc))

        state_abc = run_chain(two_characters, blocks_abc)
        state_cba = run_chain(two_characters, blocks_cba)

        # At least one pair should differ in at least one dimension
        pk = list(state_abc.pair_states.keys())[0]
        abc = state_abc.pair_states[pk]
        cba = state_cba.pair_states[pk]
        differs = (abc.t_history != cba.t_history or
                   abc.c_history != cba.c_history or
                   abc.v_history != cba.v_history)
        assert differs, "Order should produce different trajectories"

    def test_to_dict_serializable(self, two_characters):
        blocks = [SCENARIO_BLOCKS["betrayal-revealed"]]
        state = run_chain(two_characters, blocks)
        d = state.to_dict()
        assert "pair_states" in d
        assert "block_results" in d
        assert "block_count" in d


class TestTrajectoryClassification:
    def test_stable_trajectory(self):
        ps = PairState(
            pair_key="a:b", char_a_id="a", char_b_id="b",
            char_a_name="Alpha", char_b_name="Beta",
            baseline_t=0.5, baseline_c=0.5, baseline_v=0.2,
            t_history=[0.51, 0.50, 0.52],
            c_history=[0.50, 0.51, 0.50],
            v_history=[0.20, 0.21, 0.20],
            label_history=["Interesting tension", "Interesting tension", "Interesting tension"],
        )
        arc = classify_trajectory(ps)
        assert arc.arc_type == "stable"

    def test_transforming_trajectory(self):
        ps = PairState(
            pair_key="a:b", char_a_id="a", char_b_id="b",
            char_a_name="Alpha", char_b_name="Beta",
            baseline_t=0.3, baseline_c=0.3, baseline_v=0.2,
            t_history=[0.5, 0.7, 0.8],
            c_history=[0.3, 0.5, 0.6],
            v_history=[0.2, 0.3, 0.3],
            label_history=["Interesting tension", "Explosive but rewarding", "Explosive but rewarding"],
        )
        arc = classify_trajectory(ps)
        assert arc.arc_type == "transforming"

    def test_empty_history_is_stable(self):
        ps = PairState(
            pair_key="a:b", char_a_id="a", char_b_id="b",
            char_a_name="Alpha", char_b_name="Beta",
            baseline_t=0.5, baseline_c=0.5, baseline_v=0.2,
        )
        arc = classify_trajectory(ps)
        assert arc.arc_type == "stable"

    def test_arc_to_dict(self):
        ps = PairState(
            pair_key="a:b", char_a_id="a", char_b_id="b",
            char_a_name="Alpha", char_b_name="Beta",
            baseline_t=0.5, baseline_c=0.5, baseline_v=0.2,
            t_history=[0.5], c_history=[0.5], v_history=[0.2],
            label_history=["Interesting tension"],
        )
        arc = classify_trajectory(ps)
        d = arc.to_dict()
        assert "arc_type" in d
        assert "before_tcv" in d
        assert "after_tcv" in d


class TestChainSummary:
    def test_summarize_produces_valid_output(self, two_characters):
        blocks = [SCENARIO_BLOCKS[b] for b in ["betrayal-revealed", "resources-run-dry"]]
        state = run_chain(two_characters, blocks)
        summary = summarize_chain(state)
        assert summary.party_trajectory
        assert len(summary.pair_trajectories) == 1

    def test_summary_to_dict(self, two_characters):
        blocks = [SCENARIO_BLOCKS["betrayal-revealed"]]
        state = run_chain(two_characters, blocks)
        summary = summarize_chain(state)
        d = summary.to_dict()
        assert "pair_trajectories" in d
        assert "critical_block" in d
        assert "party_trajectory" in d
