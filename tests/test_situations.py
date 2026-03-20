"""Situation catalog validation tests.

Verifies that all situation entries reference valid primitives
and maintain internal consistency.
"""

import pytest
from archetypes_core.primitives import PRIMITIVES
from archetypes_core.situations import SITUATIONS, SITUATION_CATEGORIES


class TestSituationCatalog:
    def test_has_situations(self):
        assert len(SITUATIONS) >= 39

    def test_has_categories(self):
        assert len(SITUATION_CATEGORIES) == 6

    def test_all_situations_have_required_fields(self):
        required = {"name", "category", "essence", "pressure_targets",
                     "shadow_activators", "intensity", "escalation_pattern"}
        for sid, sit in SITUATIONS.items():
            missing = required - set(sit.keys())
            assert not missing, f"Situation {sid} missing fields: {missing}"

    def test_pressure_targets_reference_valid_primitives(self):
        """Every pressure_target.primitive_id must exist in PRIMITIVES."""
        invalid = []
        for sid, sit in SITUATIONS.items():
            for pt in sit["pressure_targets"]:
                if pt["primitive_id"] not in PRIMITIVES:
                    invalid.append(f"{sid} -> {pt['primitive_id']}")
        assert not invalid, f"Invalid primitive references: {invalid}"

    def test_shadow_activators_reference_valid_primitives(self):
        """Every shadow_activator must exist in PRIMITIVES."""
        invalid = []
        for sid, sit in SITUATIONS.items():
            for sa in sit["shadow_activators"]:
                if sa not in PRIMITIVES:
                    invalid.append(f"{sid} -> {sa}")
        assert not invalid, f"Invalid shadow activator references: {invalid}"

    def test_intensity_values_are_valid(self):
        valid = {"low", "moderate", "high", "extreme"}
        for sid, sit in SITUATIONS.items():
            assert sit["intensity"] in valid, f"{sid} has invalid intensity: {sit['intensity']}"

    def test_escalation_pattern_values_are_valid(self):
        valid = {"slow-burn", "building", "acute", "cyclical"}
        for sid, sit in SITUATIONS.items():
            assert sit["escalation_pattern"] in valid, f"{sid} has invalid pattern: {sit['escalation_pattern']}"

    def test_category_counts_match(self):
        """SITUATION_CATEGORIES count should match actual situations."""
        actual_counts = {}
        for sit in SITUATIONS.values():
            cat = sit["category"]
            actual_counts[cat] = actual_counts.get(cat, 0) + 1

        for cat_id, cat_meta in SITUATION_CATEGORIES.items():
            assert cat_meta["count"] == actual_counts.get(cat_id, 0), \
                f"Category {cat_id}: expected {cat_meta['count']}, got {actual_counts.get(cat_id, 0)}"

    def test_complementary_situations_exist(self):
        """All complementary_situations references should be valid situation IDs."""
        invalid = []
        for sid, sit in SITUATIONS.items():
            for ref in sit.get("complementary_situations", []):
                if ref not in SITUATIONS:
                    invalid.append(f"{sid} -> {ref}")
        assert not invalid, f"Dangling complementary_situations: {invalid}"

    def test_tension_situations_exist(self):
        """All tension_situations references should be valid situation IDs."""
        invalid = []
        for sid, sit in SITUATIONS.items():
            for ref in sit.get("tension_situations", []):
                if ref not in SITUATIONS:
                    invalid.append(f"{sid} -> {ref}")
        assert not invalid, f"Dangling tension_situations: {invalid}"
