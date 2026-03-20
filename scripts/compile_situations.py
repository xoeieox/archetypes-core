#!/usr/bin/env python3
"""Compile situation YAML cards into archetypes_core/situations/catalog.py.

Reads all situation YAML cards from the AI framework and generates a
flat dict catalog for the engine to use at runtime (no YAML parsing needed).
"""

import sys
from pathlib import Path

import yaml

CARDS_DIR = Path("/srv/git/archetypal-intelligence-working/cards/situations")
OUTPUT = Path(__file__).parent.parent / "archetypes_core" / "situations" / "catalog.py"

CATEGORY_META = {
    "resource-pressure": {"name": "Resource Pressure"},
    "moral-dilemma": {"name": "Moral Dilemma"},
    "power-dynamics": {"name": "Power Dynamics"},
    "temporal-pressure": {"name": "Temporal Pressure"},
    "identity-threat": {"name": "Identity Threat"},
    "relational-tension": {"name": "Relational Tension"},
}


def load_situation(path: Path) -> dict:
    with open(path) as f:
        data = yaml.safe_load(f)
    return data


def format_string(s: str) -> str:
    """Escape for Python string repr."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def main():
    situations = {}
    errors = []

    for category_dir in sorted(CARDS_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        for yaml_file in sorted(category_dir.glob("*.yaml")):
            try:
                data = load_situation(yaml_file)
                sid = data["situation_id"]

                pressure_targets = []
                for pt in data.get("pressure_targets", []):
                    pressure_targets.append({
                        "primitive_id": pt["primitive_id"],
                        "activation": pt["activation"],
                    })

                dynamics = data.get("dynamics", {})

                situations[sid] = {
                    "name": data["name"],
                    "category": data["category"],
                    "essence": data["pattern"]["essence"],
                    "psychological_pressure": data["pattern"]["psychological_pressure"],
                    "shadow_trigger": data["pattern"]["shadow_trigger"],
                    "observable_markers": data["pattern"].get("observable_markers", []),
                    "pressure_targets": pressure_targets,
                    "shadow_activators": data.get("shadow_activators", []),
                    "intensity": dynamics.get("intensity", "moderate"),
                    "escalation_pattern": dynamics.get("escalation_pattern", "building"),
                    "complementary_situations": dynamics.get("complementary_situations", []),
                    "tension_situations": dynamics.get("tension_situations", []),
                    "agent_prompt_fragment": data.get("agent_prompt_fragment", ""),
                }
            except Exception as e:
                errors.append(f"  {yaml_file.name}: {e}")

    # Generate catalog.py
    lines = [
        '"""',
        "Situation Primitives Catalog — auto-generated from YAML cards.",
        "",
        f"Total: {len(situations)} situations across {len(CATEGORY_META)} categories.",
        "",
        "DO NOT EDIT MANUALLY. Regenerate with: python scripts/compile_situations.py",
        '"""',
        "",
        "",
        "SITUATIONS = {",
    ]

    for sid in sorted(situations.keys()):
        s = situations[sid]
        lines.append(f'    "{sid}": {{')
        lines.append(f'        "name": "{format_string(s["name"])}",')
        lines.append(f'        "category": "{s["category"]}",')
        lines.append(f'        "essence": "{format_string(s["essence"])}",')
        lines.append(f'        "psychological_pressure": "{format_string(s["psychological_pressure"])}",')
        lines.append(f'        "shadow_trigger": "{format_string(s["shadow_trigger"])}",')

        # observable_markers
        lines.append(f'        "observable_markers": [')
        for marker in s["observable_markers"]:
            lines.append(f'            "{format_string(marker)}",')
        lines.append(f'        ],')

        # pressure_targets
        lines.append(f'        "pressure_targets": [')
        for pt in s["pressure_targets"]:
            lines.append(f'            {{"primitive_id": "{pt["primitive_id"]}", "activation": "{format_string(pt["activation"])}"}},')
        lines.append(f'        ],')

        # shadow_activators
        sa_str = ", ".join(f'"{x}"' for x in s["shadow_activators"])
        lines.append(f'        "shadow_activators": [{sa_str}],')

        lines.append(f'        "intensity": "{s["intensity"]}",')
        lines.append(f'        "escalation_pattern": "{s["escalation_pattern"]}",')

        cs_str = ", ".join(f'"{x}"' for x in s["complementary_situations"])
        lines.append(f'        "complementary_situations": [{cs_str}],')

        ts_str = ", ".join(f'"{x}"' for x in s["tension_situations"])
        lines.append(f'        "tension_situations": [{ts_str}],')

        lines.append(f'    }},')

    lines.append("}")
    lines.append("")
    lines.append("")

    # SITUATION_CATEGORIES
    lines.append("SITUATION_CATEGORIES = {")
    for cat_id, meta in sorted(CATEGORY_META.items()):
        count = sum(1 for s in situations.values() if s["category"] == cat_id)
        lines.append(f'    "{cat_id}": {{"name": "{meta["name"]}", "count": {count}}},')
    lines.append("}")
    lines.append("")

    OUTPUT.write_text("\n".join(lines))

    # Summary
    print(f"Generated {OUTPUT}")
    print(f"  Total situations: {len(situations)}")
    by_cat = {}
    for s in situations.values():
        by_cat.setdefault(s["category"], 0)
        by_cat[s["category"]] += 1
    for cat in sorted(by_cat):
        print(f"    {cat}: {by_cat[cat]}")

    if errors:
        print(f"\n  Errors ({len(errors)}):")
        for e in errors:
            print(f"    {e}")

    # Check for dangling situation cross-references
    all_sids = set(situations.keys())
    dangling = set()
    for sid, s in situations.items():
        for ref in s["complementary_situations"] + s["tension_situations"]:
            if ref not in all_sids:
                dangling.add(f"{sid} references unknown situation: {ref}")
    if dangling:
        print(f"\n  Dangling situation references ({len(dangling)}):")
        for d in sorted(dangling):
            print(f"    {d}")


if __name__ == "__main__":
    main()
