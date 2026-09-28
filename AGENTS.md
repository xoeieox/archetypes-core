# AGENTS.md - working notes for AI agents in this repo

archetypes-core is the **Archetypal Intelligence engine**: a curated catalog
of behavioral and situation primitives plus pure-computation scoring
(T/C/V), simulation (chains, parties, pressure), and relationship
trajectory modules. The catalog is the substance; the engine reads it.

## Hard rules

- **Pure computation. No LLM calls, no network I/O, no web framework
  imports.** The only runtime dependency is `pydantic`. If a change would
  add another, stop and brief the owner.
- The catalog modules (`primitives/catalog.py`, `situations/catalog.py`)
  are generated from YAML cards - never hand-edit them; regenerate via
  `scripts/compile_primitives.py` / `scripts/compile_situations.py`.
- Engine changes must not silently change scoring for existing cards: run
  the full suite and call out any score shifts in the PR description as
  intended semantic changes.
- Conventional commits (`feat(scope): ...`, `fix(scope): ...`).

## Dev loop

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
pytest
```
