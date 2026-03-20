#!/usr/bin/env python3
"""Compile primitive YAML cards into archetypes_core catalog.py.

Reads all 72 YAML primitive cards and Kyma's existing shadow_volatility
values, then generates a clean Python catalog module with PRIMITIVES and
CATEGORIES dicts.
"""

from __future__ import annotations

import ast
import os
import sys
import textwrap
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CARDS_DIR = Path("/srv/git/archetypal-intelligence-working/cards/primitives")
KYMA_PRIMITIVES = Path("/data/kyma/primitives.py")
OUTPUT_DIR = Path("/srv/git/archetypes-core/archetypes_core/primitives")
OUTPUT_FILE = OUTPUT_DIR / "catalog.py"

# Category subdirs expected
CATEGORY_DIRS = [
    "behavioral",
    "cognitive",
    "coping",
    "emotional",
    "growth-shadow",
    "relational",
    "values",
]

# Default shadow_volatility for new primitives (not in Kyma) by category
CATEGORY_DEFAULTS: dict[str, float] = {
    "cognitive": 0.2,
    "emotional": 0.4,
    "behavioral": 0.3,
    "coping": 0.25,
    "values": 0.3,
    "growth-shadow": 0.5,
    "relational": 0.35,
}

# Category metadata
CATEGORIES = {
    "cognitive": {"name": "Cognitive", "color": "#4A90D9", "dark": "#2C5F8A"},
    "emotional": {"name": "Emotional", "color": "#E74C3C", "dark": "#A93226"},
    "behavioral": {"name": "Behavioral", "color": "#2ECC71", "dark": "#1E8449"},
    "coping": {"name": "Coping", "color": "#9B59B6", "dark": "#6C3483"},
    "values": {"name": "Values", "color": "#F39C12", "dark": "#B7770B"},
    "growth-shadow": {"name": "Growth & Shadow", "color": "#1ABC9C", "dark": "#148F77"},
    "relational": {"name": "Relational", "color": "#E67E22", "dark": "#BA6418"},
}


# ---------------------------------------------------------------------------
# Extract Kyma shadow_volatility values
# ---------------------------------------------------------------------------
def load_kyma_volatilities() -> dict[str, float]:
    """Parse Kyma's primitives.py and extract shadow_volatility per ID."""
    source = KYMA_PRIMITIVES.read_text()

    # Parse the file as AST to safely extract the PRIMITIVES dict
    tree = ast.parse(source)
    result: dict[str, float] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PRIMITIVES":
                    # Evaluate the dict literal
                    primitives = ast.literal_eval(node.value)
                    for pid, pdata in primitives.items():
                        if "shadow_volatility" in pdata:
                            result[pid] = pdata["shadow_volatility"]
                    return result

    return result


# ---------------------------------------------------------------------------
# Load YAML cards
# ---------------------------------------------------------------------------
def load_yaml_cards() -> list[dict]:
    """Load all YAML primitive cards from subdirectories."""
    cards = []
    for cat_dir in CATEGORY_DIRS:
        dir_path = CARDS_DIR / cat_dir
        if not dir_path.exists():
            print(f"  WARNING: Category directory not found: {dir_path}")
            continue
        for yaml_file in sorted(dir_path.glob("*.yaml")):
            with open(yaml_file) as f:
                card = yaml.safe_load(f)
            if card:
                cards.append(card)
    return cards


# ---------------------------------------------------------------------------
# Generate catalog.py
# ---------------------------------------------------------------------------
def format_list(items: list[str], indent: int = 8) -> str:
    """Format a list of strings as a Python list literal."""
    if not items:
        return "[]"
    pad = " " * indent
    lines = [f'{pad}"{item}",' for item in items]
    return "[\n" + "\n".join(lines) + "\n" + " " * (indent - 4) + "]"


def generate_catalog(
    cards: list[dict],
    kyma_volatilities: dict[str, float],
) -> str:
    """Generate the catalog.py source code."""
    lines: list[str] = []
    lines.append('"""')
    lines.append("Archetypal Intelligence — Primitive Catalog (auto-generated)")
    lines.append("")
    lines.append(f"{len(cards)} behavioral primitives across {len(CATEGORY_DIRS)} categories.")
    lines.append("Each primitive defines its tension and complementary relationships")
    lines.append("with other primitives, enabling pure-computation T/C/V scoring")
    lines.append("without LLM calls.")
    lines.append("")
    lines.append("DO NOT EDIT BY HAND — regenerate with scripts/compile_primitives.py")
    lines.append('"""')
    lines.append("")
    lines.append("PRIMITIVES = {")

    # Group by category for readability
    by_category: dict[str, list[dict]] = {}
    for card in cards:
        cat = card["category"]
        by_category.setdefault(cat, []).append(card)

    for cat in CATEGORY_DIRS:
        cat_cards = by_category.get(cat, [])
        if not cat_cards:
            continue
        cat_name = CATEGORIES[cat]["name"]
        lines.append(f"    # {'=' * 73}")
        lines.append(f"    # {cat_name.upper()} ({len(cat_cards)})")
        lines.append(f"    # {'=' * 73}")

        for card in sorted(cat_cards, key=lambda c: c["card_id"]):
            card_id = card["card_id"]
            name = card["name"]
            description = card.get("pattern", {}).get("essence", "")
            tension = card.get("spectrum", {}).get("tension_primitives", [])
            complementary = card.get("spectrum", {}).get("complementary_primitives", [])

            # Shadow volatility: Kyma value or category default
            if card_id in kyma_volatilities:
                sv = kyma_volatilities[card_id]
            else:
                sv = CATEGORY_DEFAULTS.get(cat, 0.3)

            lines.append(f'    "{card_id}": {{')
            lines.append(f'        "name": "{name}",')
            lines.append(f'        "category": "{cat}",')
            # Escape any quotes in description
            desc_escaped = description.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'        "description": "{desc_escaped}",')
            lines.append(f'        "tension_with": {format_list(tension)},')
            lines.append(f'        "complementary_with": {format_list(complementary)},')
            lines.append(f'        "shadow_volatility": {sv},')
            lines.append("    },")

    lines.append("}")
    lines.append("")

    # CATEGORIES dict
    lines.append("CATEGORIES = {")
    for cat_id, cat_meta in CATEGORIES.items():
        lines.append(
            f'    "{cat_id}": '
            f'{{"name": "{cat_meta["name"]}", '
            f'"color": "{cat_meta["color"]}", '
            f'"dark": "{cat_meta["dark"]}"}},',
        )
    lines.append("}")
    lines.append("")

    # Validation function
    lines.append("")
    lines.append("def validate_primitives():")
    lines.append('    """Check all relationship references point to existing primitives."""')
    lines.append("    errors = []")
    lines.append("    ids = set(PRIMITIVES.keys())")
    lines.append("    for pid, prim in PRIMITIVES.items():")
    lines.append('        for ref in prim["tension_with"]:')
    lines.append("            if ref not in ids:")
    lines.append('                errors.append(f"{pid}: tension ref \'{ref}\' not found")')
    lines.append('        for ref in prim["complementary_with"]:')
    lines.append("            if ref not in ids:")
    lines.append('                errors.append(f"{pid}: complementary ref \'{ref}\' not found")')
    lines.append("    return errors")
    lines.append("")
    lines.append("")
    lines.append('if __name__ == "__main__":')
    lines.append("    errors = validate_primitives()")
    lines.append("    if errors:")
    lines.append('        print("VALIDATION ERRORS:")')
    lines.append("        for e in errors:")
    lines.append('            print(f"  - {e}")')
    lines.append("    else:")
    lines.append('        print(f"All {len(PRIMITIVES)} primitives valid.")')
    lines.append("        for cat_id, cat in CATEGORIES.items():")
    lines.append(
        "            count = sum(1 for p in PRIMITIVES.values()"
        ' if p["category"] == cat_id)'
    )
    lines.append('            print(f"  {cat[\'name\']}: {count}")')
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Compile Primitives — YAML → catalog.py")
    print("=" * 60)

    # 1. Load Kyma volatilities
    print(f"\nReading Kyma primitives from {KYMA_PRIMITIVES}...")
    kyma_vol = load_kyma_volatilities()
    print(f"  Found {len(kyma_vol)} primitives with shadow_volatility values")

    # 2. Load YAML cards
    print(f"\nReading YAML cards from {CARDS_DIR}...")
    cards = load_yaml_cards()
    print(f"  Loaded {len(cards)} primitive cards")

    # 3. Identify new primitives
    card_ids = {c["card_id"] for c in cards}
    kyma_ids = set(kyma_vol.keys())
    new_ids = card_ids - kyma_ids
    removed_ids = kyma_ids - card_ids

    print(f"\n--- Summary ---")
    print(f"  Total primitives: {len(cards)}")
    print(f"  From Kyma (shadow_volatility carried over): {len(card_ids & kyma_ids)}")
    print(f"  New primitives (category default volatility): {len(new_ids)}")
    if new_ids:
        for nid in sorted(new_ids):
            cat = next((c["category"] for c in cards if c["card_id"] == nid), "?")
            print(f"    + {nid} ({cat}, default {CATEGORY_DEFAULTS.get(cat, 0.3)})")
    if removed_ids:
        print(f"  In Kyma but not in YAML cards: {len(removed_ids)}")
        for rid in sorted(removed_ids):
            print(f"    - {rid}")

    # 4. Check for missing references
    all_ids = card_ids
    missing_refs = []
    for card in cards:
        cid = card["card_id"]
        for ref in card.get("spectrum", {}).get("tension_primitives", []):
            if ref not in all_ids:
                missing_refs.append((cid, "tension", ref))
        for ref in card.get("spectrum", {}).get("complementary_primitives", []):
            if ref not in all_ids:
                missing_refs.append((cid, "complementary", ref))

    if missing_refs:
        print(f"\n  Missing references ({len(missing_refs)}):")
        for cid, rel_type, ref in sorted(missing_refs):
            print(f"    {cid} -> {rel_type}: {ref}")
    else:
        print(f"\n  All references valid.")

    # Category breakdown
    print(f"\n--- By Category ---")
    by_cat: dict[str, int] = {}
    for card in cards:
        by_cat[card["category"]] = by_cat.get(card["category"], 0) + 1
    for cat in CATEGORY_DIRS:
        count = by_cat.get(cat, 0)
        print(f"  {CATEGORIES[cat]['name']}: {count}")

    # 5. Generate and write catalog.py
    print(f"\nGenerating {OUTPUT_FILE}...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source = generate_catalog(cards, kyma_vol)
    OUTPUT_FILE.write_text(source)
    print(f"  Written ({len(source)} bytes)")

    # 6. Verify the generated file is valid Python
    print(f"\nVerifying generated file...")
    try:
        compile(source, str(OUTPUT_FILE), "exec")
        print("  Syntax OK")
    except SyntaxError as e:
        print(f"  SYNTAX ERROR: {e}")
        sys.exit(1)

    print(f"\nDone.")


if __name__ == "__main__":
    main()
