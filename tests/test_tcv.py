"""T/C/V engine regression tests.

These tests verify that the archetypes-core engine produces scores
consistent with Kyma's original engine. Note: scores may differ from
the Kyma baseline because the primitive catalog has been updated to
the framework's canonical 72 primitives (with different tension_with
and complementary_with relationships for some entries).

The tests verify structural correctness and score bounds, not exact
match to Kyma's historical values.
"""

import pytest
from archetypes_core.engine import (
    compute_tension,
    compute_complementarity,
    compute_volatility,
    compute_pair_scores,
    compute_party_matrix,
    classify_pair,
)


class TestPairScoring:
    def test_scores_are_bounded(self, sample_characters):
        char_a, char_b = sample_characters
        result = compute_pair_scores(char_a, char_b)
        assert 0.0 <= result["t"] <= 1.0
        assert 0.0 <= result["c"] <= 1.0
        assert 0.0 <= result["v"] <= 1.0

    def test_pair_has_required_fields(self, sample_characters):
        char_a, char_b = sample_characters
        result = compute_pair_scores(char_a, char_b)
        assert result["a"] == "test-warrior"
        assert result["b"] == "test-trickster"
        assert "label" in result
        assert "tension_detail" in result
        assert "complementarity_detail" in result
        assert "volatility_detail" in result

    def test_tension_is_symmetric(self, sample_characters):
        char_a, char_b = sample_characters
        t_ab, _ = compute_tension(char_a, char_b)
        t_ba, _ = compute_tension(char_b, char_a)
        assert t_ab == t_ba

    def test_complementarity_is_symmetric(self, sample_characters):
        char_a, char_b = sample_characters
        c_ab, _ = compute_complementarity(char_a, char_b)
        c_ba, _ = compute_complementarity(char_b, char_a)
        assert c_ab == c_ba

    def test_volatility_contributors_labeled(self, sample_characters):
        char_a, char_b = sample_characters
        _, contributors = compute_volatility(char_a, char_b)
        sources = {c["source"] for c in contributors}
        # Both sides should contribute shadows
        assert "a_shadow" in sources or "b_shadow" in sources

    def test_custom_scales(self, sample_characters):
        char_a, char_b = sample_characters
        r1 = compute_pair_scores(char_a, char_b, t_scale=1.0)
        r2 = compute_pair_scores(char_a, char_b, t_scale=10.0)
        # Higher scale should produce equal or higher tension
        assert r2["t"] >= r1["t"]

    def test_identical_characters_have_no_tension(self):
        char = {
            "id": "same",
            "name": "Same",
            "primary": [{"primitive_id": "duty-over-desire", "weight": 1.0}],
            "shadow": [],
        }
        t, _ = compute_tension(char, char)
        assert t == 0.0  # A primitive can't be in tension with itself


class TestClassifyPair:
    def test_high_volatility(self):
        label = classify_pair(0.3, 0.3, 0.7)
        assert label["label"] == "Unpredictable"

    def test_explosive(self):
        label = classify_pair(0.7, 0.7, 0.3)
        assert label["label"] == "Explosive but rewarding"

    def test_straight_conflict(self):
        label = classify_pair(0.7, 0.2, 0.3)
        assert label["label"] == "Straight conflict"

    def test_reliable_partnership(self):
        label = classify_pair(0.2, 0.7, 0.3)
        assert label["label"] == "Reliable partnership"

    def test_little_charge(self):
        label = classify_pair(0.1, 0.1, 0.1)
        assert label["label"] == "Little dynamic charge"


class TestPartyMatrix:
    def test_party_of_two(self, sample_characters):
        char_a, char_b = sample_characters
        result = compute_party_matrix([char_a, char_b])
        assert len(result["pairs"]) == 1
        assert "aggregates" in result
        assert "highlights" in result

    def test_party_of_five_produces_10_pairs(self, kyma_premade_characters):
        chars = kyma_premade_characters[:5]
        result = compute_party_matrix(chars)
        assert len(result["pairs"]) == 10  # 5 choose 2

    def test_full_roster_produces_45_pairs(self, kyma_premade_characters):
        result = compute_party_matrix(kyma_premade_characters)
        assert len(result["pairs"]) == 45  # 10 choose 2

    def test_all_scores_bounded(self, kyma_premade_characters):
        result = compute_party_matrix(kyma_premade_characters)
        for pair in result["pairs"]:
            assert 0.0 <= pair["t"] <= 1.0, f"{pair['a_name']}+{pair['b_name']} T={pair['t']}"
            assert 0.0 <= pair["c"] <= 1.0, f"{pair['a_name']}+{pair['b_name']} C={pair['c']}"
            assert 0.0 <= pair["v"] <= 1.0, f"{pair['a_name']}+{pair['b_name']} V={pair['v']}"

    def test_aggregates_are_means(self, kyma_premade_characters):
        result = compute_party_matrix(kyma_premade_characters[:3])
        pairs = result["pairs"]
        expected_mean_t = round(sum(p["t"] for p in pairs) / len(pairs), 3)
        assert result["aggregates"]["mean_t"] == expected_mean_t

    def test_empty_party(self):
        result = compute_party_matrix([])
        assert result["pairs"] == []

    def test_single_character(self, sample_characters):
        char_a, _ = sample_characters
        result = compute_party_matrix([char_a])
        assert result["pairs"] == []

    def test_score_spread(self, kyma_premade_characters):
        """Verify the catalog produces meaningful score spread, not all zeros or all ones."""
        result = compute_party_matrix(kyma_premade_characters)
        t_scores = [p["t"] for p in result["pairs"]]
        c_scores = [p["c"] for p in result["pairs"]]
        # Should have some variation
        assert max(t_scores) - min(t_scores) > 0.3, "Tension scores too flat"
        assert max(c_scores) - min(c_scores) > 0.3, "Complementarity scores too flat"
        # Should use a reasonable range
        assert max(t_scores) > 0.5, "No high tension pairs found"
        assert max(c_scores) > 0.5, "No high complementarity pairs found"
