"""Pydantic models for Primitive archetype cards.

Standalone model definitions adapted from the Archetypal Intelligence framework.
No dependencies on the broader framework — just data shapes.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class PrimitiveCategory(str, Enum):
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    BEHAVIORAL = "behavioral"
    COPING = "coping"
    VALUES = "values"
    GROWTH_SHADOW = "growth-shadow"
    RELATIONAL = "relational"


class RiskTolerance(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VARIABLE = "variable"


class TimePreference(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    VARIABLE = "variable"


class Pattern(BaseModel):
    essence: str
    observable_indicators: list[str]
    internal_experience: str
    shadow_manifestation: str


class Spectrum(BaseModel):
    healthy_expression: str
    unhealthy_expression: str
    complementary_primitives: list[str] = []
    tension_primitives: list[str] = []


class DecisionMaking(BaseModel):
    approach: str
    risk_tolerance: RiskTolerance
    time_preference: TimePreference


class InteractionPatterns(BaseModel):
    conflict: str
    collaboration: str


class DialogueIndicators(BaseModel):
    tone: str
    example_phrases: list[str]


class Behavior(BaseModel):
    decision_making: DecisionMaking
    interaction_patterns: InteractionPatterns
    dialogue_indicators: DialogueIndicators


class PressureResponse(BaseModel):
    """How this primitive manifests under resource pressure.

    Generic (not resource-specific) -- describes behavioral shifts under
    scarcity vs abundance conditions.  The specific resource context
    comes from the scenario.
    """

    scarcity_behavior: str
    abundance_behavior: str
    resource_priority: str


class CharacterExample(BaseModel):
    character_id: str
    weight: float = Field(ge=0.0, le=1.0)
    manifestation_note: str


class CulturalProvenance(BaseModel):
    """Cross-cultural origin for a primitive."""

    tradition: str
    term: str
    nuance: str


class PrimitiveCard(BaseModel):
    """A universal behavioral building block.

    Full YAML card representation including all pattern, spectrum,
    behavior, and metadata fields.
    """

    card_id: str
    version: str
    category: PrimitiveCategory
    name: str
    pattern: Pattern
    spectrum: Spectrum
    behavior: Behavior
    agent_prompt_fragment: str
    character_examples: list[CharacterExample] = Field(min_length=1)
    tags: list[str]
    contributed_by: str
    date_added: str

    @field_validator("date_added", mode="before")
    @classmethod
    def coerce_date_to_str(cls, v: object) -> str:
        return str(v)

    # Optional fields
    cultural_universality_notes: str | None = None
    source_references: list[str] | None = None
    pressure_response: PressureResponse | None = None
    cross_cultural_provenance: list[CulturalProvenance] | None = None


class CatalogEntry(BaseModel):
    """Lightweight primitive entry as stored in catalog.py PRIMITIVES dict."""

    name: str
    category: PrimitiveCategory
    description: str
    tension_with: list[str] = []
    complementary_with: list[str] = []
    shadow_volatility: float = Field(ge=0.0, le=1.0)


class CategoryMeta(BaseModel):
    """Display metadata for a primitive category."""

    name: str
    color: str
    dark: str
