"""Central balance and merchant data for Sword Phantasia."""

from dataclasses import dataclass

INVENTORY_SLOT_LIMIT = 30
MAX_UPGRADE_LEVEL = 5
UPGRADE_DAMAGE_PER_LEVEL = 0.15
FORGE_BASE_COST = 30
FORGE_TIER_COST = 35
FORGE_DAMAGE_COST_MULTIPLIER = 1.2
FORGE_RARITY_MULTIPLIERS = {
    "Common": 1.0,
    "Uncommon": 1.1,
    "Rare": 1.25,
    "Epic": 1.5,
    "Legendary": 1.75,
}

RARITY_SALVAGE = {
    "Common": 1,
    "Uncommon": 2,
    "Rare": 4,
    "Epic": 7,
    "Legendary": 12,
}

COMBAT = {
    "critical_chance": 0.15,
    "critical_multiplier": 1.5,
    "defend_mp_recovery": 14,
    "heavy_defend_bonus_mp": 6,
    "defend_damage_multiplier": 0.5,
    "opening_damage_bonus": 1.25,
    "heavy_intent_threshold": 1.35,
}

DIFFICULTY_PROFILES = {
    "Easy": {
        "enemy_hp": 0.80,
        "enemy_damage": 0.75,
        "player_damage": 1.15,
        "rewards": 1.00,
        "defeat_gold_loss": 0.10,
    },
    "Normal": {
        "enemy_hp": 1.00,
        "enemy_damage": 1.00,
        "player_damage": 1.00,
        "rewards": 1.00,
        "defeat_gold_loss": 0.15,
    },
    "Hard": {
        "enemy_hp": 1.30,
        "enemy_damage": 1.25,
        "player_damage": 0.90,
        "rewards": 1.25,
        "defeat_gold_loss": 0.20,
    },
}

TEXT_SPEED_MULTIPLIERS = {"Fast": 0.60, "Normal": 1.00, "Slow": 1.45}


@dataclass(frozen=True)
class ShopEntry:
    name: str
    attributes: str
    cost: int
    damage: float = 0.0
    consumable: bool = False
    heal: int = 0
    armor: bool = False
    defense: float = 0.0
    rarity: str = "Common"

    def create_item(self):
        from item import Item
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


SHOP_INVENTORY = (
    ShopEntry("Iron Sword", "Sturdy", 30, damage=15.0),
    ShopEntry("Steel Axe", "Heavy", 50, damage=20.0),
    ShopEntry("Excalibur", "Legendary", 200, damage=50.0, rarity="Legendary"),
    ShopEntry("Healing Potion", "Consumable", 15, consumable=True, heal=50),
    ShopEntry("Leather Armor", "Light", 40, armor=True, defense=5.0),
    ShopEntry("Iron Armor", "Sturdy", 100, armor=True, defense=12.0),
)


def difficulty_profile(name):
    return DIFFICULTY_PROFILES.get(name, DIFFICULTY_PROFILES["Normal"])


def scale_enemy_stats(hp, attack, difficulty):
    profile = difficulty_profile(difficulty)
    return max(1, int(round(hp * profile["enemy_hp"]))), max(1, int(round(attack * profile["enemy_damage"])))


def scale_player_damage(damage, difficulty):
    return max(1, int(round(damage * difficulty_profile(difficulty)["player_damage"])))


def scale_rewards(exp, gold, difficulty):
    multiplier = difficulty_profile(difficulty)["rewards"]
    return max(0, int(round(exp * multiplier))), max(0, int(round(gold * multiplier)))
