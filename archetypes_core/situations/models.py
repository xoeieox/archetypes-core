"""Pydantic models for Situation Primitive cards.

Adapted from the Archetypal Intelligence framework.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class SituationCategory(str, Enum):
    RESOURCE_PRESSURE = "resource-pressure"
    MORAL_DILEMMA = "moral-dilemma"
    POWER_DYNAMICS = "power-dynamics"
    TEMPORAL_PRESSURE = "temporal-pressure"
    IDENTITY_THREAT = "identity-threat"
    RELATIONAL_TENSION = "relational-tension"


class Intensity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class EscalationPattern(str, Enum):
    SLOW_BURN = "slow-burn"
    BUILDING = "building"
    ACUTE = "acute"
    CYCLICAL = "cyclical"


class SituationPattern(BaseModel):
    """The core definition of what this situation IS."""

    essence: str
    observable_markers: list[str]
    psychological_pressure: str
    shadow_trigger: str


class SituationDynamics(BaseModel):
    """How this situation unfolds over time."""

    intensity: Intensity
    escalation_pattern: EscalationPattern
    complementary_situations: list[str] = []
    tension_situations: list[str] = []


class PressureTarget(BaseModel):
    """A behavioral primitive this situation is designed to stress."""

    primitive_id: str
    activation: str


class ScenarioExample(BaseModel):
    """A concrete scenario where this situation primitive manifests."""

    scenario_description: str
    setting: str
    manifestation_note: str


class SituationPrimitive(BaseModel):
    """A universal situational building block for scenario composition."""

    situation_id: str
    version: str
    category: SituationCategory
    name: str
    pattern: SituationPattern
    dynamics: SituationDynamics
    pressure_targets: list[PressureTarget] = Field(min_length=1)
    shadow_activators: list[str]
    agent_prompt_fragment: str
    scenario_examples: list[ScenarioExample] = Field(min_length=1)
    tags: list[str]
    contributed_by: str
    date_added: str

    @field_validator("date_added", mode="before")
    @classmethod
    def coerce_date_to_str(cls, v: object) -> str:
        return str(v)

    # Optional fields
    moral_dimension: str | None = None
    resource_implications: str | None = None
