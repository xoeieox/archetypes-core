# archetypes-core

**Archetypal Intelligence, made computable.** A pure-computation behavioral
engine: a curated catalog of behavioral primitives and situation primitives,
plus scoring and simulation modules that operate on them deterministically.
No LLM calls. No web framework. No I/O.

The thesis of Archetypal Intelligence is that character behavior decomposes
into a finite, inspectable set of primitives - and that interactions between
characters (and between characters and situations) can be scored and
simulated without a model in the loop. This package is the engine and the
catalog that implement that thesis.

## What's in the box

- **`primitives/`** - the primitive catalog: 88 behavioral primitives across
  7 categories, each with its tension and complementary relationships to
  other primitives, plus shadow variants. Auto-generated from a YAML card
  library; the compiled catalog is committed (see `scripts/`).
- **`situations/`** - the situation-primitive catalog: 39 situations across
  6 categories, used to model environmental pressure.
- **`engine/`** - the scoring core:
  - `tcv.py` - per-pair **T/C/V** scores: Tension (opposing primitives
    create friction), Complementarity (synergistic primitives create mutual
    strength), Volatility.
  - `chain.py` - plot-simulation chains: sequence pair states over time.
  - `party.py` - multi-party composition.
  - `pressure.py` - situation pressure applied to pair/party states.
- **`relationships/`** - relationship trajectory classification: how a
  pair's relationship evolves across a chain, from `PairState` output.
- **`drift/`** - drift analysis and lineage: tracking how compositions
  diverge over simulated time.
- **`scenarios/`** - scenario blocks for assembling simulations.
- **`corroboration.py`, `provenance.py`** - evidence/ref tracking for
  primitive assignments.
- **`world_primitives.py`** - world-scale primitives: themes and isomorphic
  links, the same decomposition applied at the substrate layer (deities,
  factions, and heroes as compositions of themes; domains mirroring each
  other through shared primitives).
- **`gpu/interface.py`** - an abstract GPU-coordination interface with a
  no-op default, so products on shared GPUs can subclass it without the
  engine caring.

## Install

Requires Python >= 3.11. The only dependency is `pydantic>=2`.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
```

## Quickstart

```python
from archetypes_core.primitives.catalog import PRIMITIVES, CATEGORIES
from archetypes_core.situations.catalog import SITUATIONS

len(PRIMITIVES)   # 88 behavioral primitives
len(CATEGORIES)   # 7 primitive categories
len(SITUATIONS)   # 39 situation primitives
```

For worked scoring and simulation examples, see `tests/test_tcv.py` and
`tests/test_situations.py`.

## Tests

```bash
pytest
```

## Catalog generators

The catalogs under `primitives/` and `situations/` are generated modules,
not hand-written - do not edit them directly. The generators ship in
`scripts/` (`compile_primitives.py`, `compile_situations.py`) for
provenance; they read the YAML card library and regenerate the committed
Python catalogs. The compiled catalogs are in-tree, so nothing outside this
repo is needed to use or develop the engine.

## Why this is public

The Archetypal Intelligence work - behavioral primitives informing AI
character reasoning, with deterministic, auditable scoring rather than
opaque model judgment - is a research direction, not a trade secret. The
catalog is the substance; the engine is straightforward given it. If you
build with it, we would like to hear where it goes.

## License

MIT - see [LICENSE](LICENSE).
