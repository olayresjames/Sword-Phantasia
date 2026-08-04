from dataclasses import dataclass
import random

from item import Item


RARITY_COLORS = {
    "Common": "#aeb8cc",
    "Uncommon": "#67dca5",
    "Rare": "#72baff",
    "Epic": "#c49cff",
    "Legendary": "#ffd166",
}


@dataclass(frozen=True)
class LootEntry:
    name: str
    attributes: str
    rarity: str
    weight: int
    damage: float = 0.0
    consumable: bool = False
    heal: int = 0
    armor: bool = False
    defense: float = 0.0

    def create_item(self):
        return Item(
            self.name,
            self.attributes,
            self.damage,
            is_consumable=self.consumable,
            heal_amount=self.heal,
            is_armor=self.armor,
            defense_bonus=self.defense,
            rarity=self.rarity,
        )


REGION_LOOT = {
    "frontier": (
        LootEntry("Traveler's Tonic", "Restorative", "Common", 34, consumable=True, heal=35),
        LootEntry("Gel-Edge Dagger", "Elastic", "Common", 30, damage=11.0),
        LootEntry("Silvergrass Mail", "Windwoven", "Uncommon", 21, armor=True, defense=5.0),
        LootEntry("Crown of Tides", "Slimeforged", "Rare", 10, damage=22.0),
        LootEntry("Prismatic Gel", "Full Restore", "Epic", 5, consumable=True, heal=100),
    ),
    "mosswood": (
        LootEntry("Mooncap Poultice", "Restorative", "Common", 34, consumable=True, heal=55),
        LootEntry("Thornwood Bow", "Barbed", "Common", 30, damage=20.0),
        LootEntry("Briarhide Coat", "Living Armor", "Uncommon", 21, armor=True, defense=9.0),
        LootEntry("Warchief's Fang", "War-Trophy", "Rare", 10, damage=31.0),
        LootEntry("Heartwood Draught", "Full Restore", "Epic", 5, consumable=True, heal=140),
    ),
    "crypt": (
        LootEntry("Ashen Elixir", "Restorative", "Common", 34, consumable=True, heal=75),
        LootEntry("Ossuary Blade", "Grave-Touched", "Common", 30, damage=27.0),
        LootEntry("Graveplate", "Runed", "Uncommon", 21, armor=True, defense=15.0),
        LootEntry("Warden's Requiem", "Soulbound", "Rare", 10, damage=42.0),
        LootEntry("Phoenix Ash", "Full Restore", "Epic", 5, consumable=True, heal=190),
    ),
    "throne": (
        LootEntry("Void Draught", "Restorative", "Common", 32, consumable=True, heal=110),
        LootEntry("Obsidian Talon", "Abyssal", "Uncommon", 30, damage=38.0),
        LootEntry("Hellfire Carapace", "Demonforged", "Rare", 22, armor=True, defense=20.0),
        LootEntry("Eclipse Brand", "World-Ender", "Epic", 12, damage=55.0),
        LootEntry("Primordial Ember", "Full Restore", "Legendary", 4, consumable=True, heal=260),
    ),
}


MINIBOSS_LOOT = {
    "tideheart": LootEntry("Tideheart Sabre", "Champion's Relic", "Legendary", 1, damage=26.0),
    "thornlord": LootEntry("Thornlord Mantle", "Champion's Relic", "Legendary", 1, armor=True, defense=13.0),
    "bonewyrm": LootEntry("Ashen Crown", "Champion's Relic", "Legendary", 1, damage=48.0),
}


REGION_REWARDS = {
    "frontier": ((20, 38), (10, 24)),
    "mosswood": ((30, 52), (16, 34)),
    "crypt": ((42, 68), (24, 45)),
    "throne": ((58, 88), (36, 62)),
}


def roll_region_loot(region_key, rng=None):
    rng = rng or random
    entries = REGION_LOOT.get(region_key, REGION_LOOT["frontier"])
    entry = rng.choices(entries, weights=[candidate.weight for candidate in entries], k=1)[0]
    return entry.create_item()


def miniboss_loot(boss_key):
    entry = MINIBOSS_LOOT.get(boss_key)
    return entry.create_item() if entry else None


def reward_ranges(region_key):
    return REGION_REWARDS.get(region_key, REGION_REWARDS["frontier"])
