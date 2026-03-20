from .catalog import SITUATIONS, SITUATION_CATEGORIES


def get_situation(situation_id: str) -> dict | None:
    """Look up a situation by ID. Returns None if not found."""
    return SITUATIONS.get(situation_id)


__all__ = ["SITUATIONS", "SITUATION_CATEGORIES", "get_situation"]
