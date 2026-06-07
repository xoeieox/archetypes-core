"""
archetypes-core — Behavioral Intelligence Engine

Pure computation library for behavioral primitive decomposition,
T/C/V (Tension/Complementarity/Volatility) scoring, situation pressure
modeling, and relationship trajectory analysis.

No LLM calls. No web framework. No I/O.
"""

__version__ = "0.1.0"

from archetypes_core.provenance import (  # noqa: E402
    INPUT_REF_TYPES,
    SCHEMA_VERSION,
    SCHEMA_VERSION_V01,
    InputRef,
    LapisToolReturn,
    Provenance,
    UpstreamRef,
    to_lapis_return,
)
from archetypes_core.corroboration import (  # noqa: E402
    ProvenanceCapableAdapter,
    corroborate_envelope,
)

__all__ = [
    "INPUT_REF_TYPES",
    "SCHEMA_VERSION",
    "SCHEMA_VERSION_V01",
    "InputRef",
    "LapisToolReturn",
    "Provenance",
    "UpstreamRef",
    "to_lapis_return",
    "ProvenanceCapableAdapter",
    "corroborate_envelope",
]
