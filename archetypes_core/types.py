"""Shared TypedDicts for dict-based API compatibility."""

from typing import TypedDict


class PrimitiveWeight(TypedDict):
    primitive_id: str
    weight: float


class ShadowWeight(TypedDict):
    primitive_id: str
    weight: float


class EngineCharacter(TypedDict):
    id: str
    name: str
    primary: list[PrimitiveWeight]
    shadow: list[ShadowWeight]
