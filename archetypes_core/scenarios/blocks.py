"""
Pre-designed scenario blocks for Plot Sim.

Each block maps to one or more situation primitives from the catalog.
Blocks represent dramatic pressures that GMs arrange into sequences
to project how character relationships evolve.
"""

from dataclasses import dataclass, field


@dataclass
class ScenarioBlock:
    """A discrete dramatic pressure point in a plot simulation."""
    block_id: str
    name: str
    situation_ids: list[str]
    narrative_seed: str
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "block_id": self.block_id,
            "name": self.name,
            "situation_ids": self.situation_ids,
            "narrative_seed": self.narrative_seed,
            "description": self.description,
        }


SCENARIO_BLOCKS: dict[str, ScenarioBlock] = {
    "betrayal-revealed": ScenarioBlock(
        block_id="betrayal-revealed",
        name="Betrayal Revealed",
        situation_ids=["betrayal-discovery"],
        narrative_seed="Someone trusted has deceived the group. The truth is now inescapable.",
        description="Tests trust, loyalty, and justice. Forces recalibration of every relationship built on the broken assumption.",
    ),
    "resources-run-dry": ScenarioBlock(
        block_id="resources-run-dry",
        name="Resources Run Dry",
        situation_ids=["resource-scarcity"],
        narrative_seed="There is not enough. Someone will go without.",
        description="Tests cooperation vs. self-preservation. Strips away abstraction — philosophy gives way to arithmetic.",
    ),
    "power-vacuum": ScenarioBlock(
        block_id="power-vacuum",
        name="Power Vacuum",
        situation_ids=["power-imbalance", "succession-crisis"],
        narrative_seed="The old authority is gone. Who fills the void — and who resists them?",
        description="Tests ambition, duty, and manipulation. Reveals who leads, who follows, and who undermines.",
    ),
    "moral-crossroads": ScenarioBlock(
        block_id="moral-crossroads",
        name="Moral Crossroads",
        situation_ids=["means-vs-ends"],
        narrative_seed="The right outcome requires wrong methods. Or the right methods produce a terrible outcome.",
        description="Tests values under pressure. Forces characters to choose between principles and consequences.",
    ),
    "forced-alliance": ScenarioBlock(
        block_id="forced-alliance",
        name="Forced Alliance",
        situation_ids=["forced-alliance"],
        narrative_seed="Enemies must work together. The alternative is worse than cooperation.",
        description="Tests adaptability, grudges, and pragmatism. Can opposing forces find common ground under threat?",
    ),
    "loss-and-grief": ScenarioBlock(
        block_id="loss-and-grief",
        name="Loss & Grief",
        situation_ids=["loss-of-kin", "griefs-long-shadow"],
        narrative_seed="Something irreplaceable is gone. The group must continue without it.",
        description="Tests emotional bonds and resilience. Grief reveals what characters truly valued.",
    ),
    "enemy-at-the-gate": ScenarioBlock(
        block_id="enemy-at-the-gate",
        name="Enemy at the Gate",
        situation_ids=["countdown-crisis", "resource-scarcity"],
        narrative_seed="An external threat demands immediate, unified response. There is no time for debate.",
        description="Tests unity, sacrifice, and leadership. External pressure can forge bonds or expose fractures.",
    ),
    "temptation": ScenarioBlock(
        block_id="temptation",
        name="Temptation",
        situation_ids=["forbidden-knowledge", "forbidden-connection"],
        narrative_seed="Something forbidden offers power, knowledge, or fulfillment. The cost is hidden — or irrelevant to the desperate.",
        description="Tests self-control and hidden desires. Reveals shadow primitives that dormant pressures activate.",
    ),
    "identity-crisis": ScenarioBlock(
        block_id="identity-crisis",
        name="Identity Crisis",
        situation_ids=["exposed-secret", "forced-role-change"],
        narrative_seed="Who you were is no longer who you must be. The mask has cracked.",
        description="Tests core values and triggers shadow activation. Forces characters to confront the gap between self-image and reality.",
    ),
    "revelation": ScenarioBlock(
        block_id="revelation",
        name="Revelation",
        situation_ids=["loyalty-vs-truth", "exposed-secret"],
        narrative_seed="A hidden truth surfaces. Everything built on the old understanding must be re-examined.",
        description="Tests trust recalibration and worldview shifts. The truth doesn't change what happened — it changes what it meant.",
    ),
}


def get_block(block_id: str) -> ScenarioBlock | None:
    """Look up a scenario block by ID."""
    return SCENARIO_BLOCKS.get(block_id)


def list_blocks() -> list[dict]:
    """Return all blocks as dicts for API consumption."""
    return [block.to_dict() for block in SCENARIO_BLOCKS.values()]
