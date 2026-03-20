"""Test fixtures for archetypes-core."""

import sys
from pathlib import Path

import pytest

# Ensure package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_characters():
    """Two simple characters for basic T/C/V testing."""
    char_a = {
        "id": "test-warrior",
        "name": "Test Warrior",
        "primary": [
            {"primitive_id": "duty-over-desire", "weight": 0.35},
            {"primitive_id": "risk-taking", "weight": 0.30},
            {"primitive_id": "justice-seeking", "weight": 0.20},
            {"primitive_id": "stoic-acceptance", "weight": 0.15},
        ],
        "shadow": [
            {"primitive_id": "wrath", "weight": 0.15},
        ],
    }
    char_b = {
        "id": "test-trickster",
        "name": "Test Trickster",
        "primary": [
            {"primitive_id": "strategic-deception", "weight": 0.35},
            {"primitive_id": "adaptive-flexibility", "weight": 0.25},
            {"primitive_id": "lateral-thinking", "weight": 0.25},
            {"primitive_id": "humility", "weight": 0.15},
        ],
        "shadow": [
            {"primitive_id": "envy", "weight": 0.10},
        ],
    }
    return char_a, char_b


@pytest.fixture
def kyma_premade_characters():
    """Kyma's 10 premade characters, loaded from the Kyma codebase."""
    sys.path.insert(0, "/data/kyma")
    from characters import PREMADE_CHARACTERS
    if isinstance(PREMADE_CHARACTERS, dict):
        return list(PREMADE_CHARACTERS.values())
    return PREMADE_CHARACTERS
