from .catalog import PRIMITIVES, CATEGORIES


def get_primitive(primitive_id: str) -> dict | None:
    """Look up a primitive by ID. Returns None if not found."""
    return PRIMITIVES.get(primitive_id)


__all__ = ["PRIMITIVES", "CATEGORIES", "get_primitive"]
