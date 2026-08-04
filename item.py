import math

from game_data import (
    FORGE_BASE_COST,
    FORGE_DAMAGE_COST_MULTIPLIER,
    FORGE_RARITY_MULTIPLIERS,
    FORGE_TIER_COST,
    MAX_UPGRADE_LEVEL,
    UPGRADE_DAMAGE_PER_LEVEL,
)


KNOWN_BASE_DAMAGE = {
    "Sword": 10.0,
    "Bow": 8.0,
    "Axe": 12.0,
    "Iron Sword": 15.0,
    "Steel Axe": 20.0,
    "Excalibur": 50.0,
    "Rusty Dagger": 8.0,
    "Bone Club": 11.0,
    "Slime Sword": 13.0,
    "Gel-Edge Dagger": 11.0,
    "Crown of Tides": 22.0,
    "Thornwood Bow": 20.0,
    "Warchief's Fang": 31.0,
    "Ossuary Blade": 27.0,
    "Warden's Requiem": 42.0,
    "Obsidian Talon": 38.0,
    "Eclipse Brand": 55.0,
    "Tideheart Sabre": 26.0,
    "Ashen Crown": 48.0,
    "Warden Charm": 18.0,
}

KNOWN_RARITY = {
    "Excalibur": "Legendary",
    "Warden Charm": "Rare",
    "Mossguard Vest": "Uncommon",
    "Crown of Tides": "Rare",
    "Prismatic Gel": "Epic",
    "Briarhide Coat": "Uncommon",
    "Warchief's Fang": "Rare",
    "Heartwood Draught": "Epic",
    "Graveplate": "Uncommon",
    "Warden's Requiem": "Rare",
    "Phoenix Ash": "Epic",
    "Obsidian Talon": "Uncommon",
    "Hellfire Carapace": "Rare",
    "Eclipse Brand": "Epic",
    "Primordial Ember": "Legendary",
    "Tideheart Sabre": "Legendary",
    "Thornlord Mantle": "Legendary",
    "Ashen Crown": "Legendary",
}


class Item:
    def __init__(self, item_name, attributes, additional_damage, is_consumable=False, heal_amount=0, is_armor=False, defense_bonus=0.0, rarity="Common", upgrade_level=0, base_damage=None, quantity=1):
        self.item_name = item_name
        self.attributes = attributes
        self.additional_damage = additional_damage
        self.is_consumable = is_consumable
        self.heal_amount = heal_amount
        self.is_armor = is_armor
        self.defense_bonus = defense_bonus
        self.rarity = rarity
        self.upgrade_level = max(0, int(upgrade_level))
        self.base_damage = float(additional_damage if base_damage is None else base_damage)
        self.quantity = max(1, int(quantity))

    def stack_key(self):
        """Only consumables stack; equipment remains individually forgeable."""
        if not self.is_consumable:
            return None
        return (self.item_name, self.heal_amount, self.rarity)

    def power_score(self):
        return float(self.defense_bonus if self.is_armor else self.additional_damage)

    def apply_upgrades(self, percentage):
        """Compatibility wrapper for older callers; upgrades now use forge tiers."""
        return self.upgrade_weapon()

    @property
    def max_upgrade_level(self):
        return MAX_UPGRADE_LEVEL

    @property
    def is_legacy_upgrade(self):
        return self.upgrade_level > MAX_UPGRADE_LEVEL

    @property
    def at_max_upgrade(self):
        return self.upgrade_level >= MAX_UPGRADE_LEVEL

    def forge_label(self):
        prefix = "Legacy " if self.is_legacy_upgrade else ""
        return f"{prefix}+{self.upgrade_level}"

    def next_upgrade_damage(self):
        if self.at_max_upgrade or self.base_damage <= 0:
            return self.additional_damage
        next_level = self.upgrade_level + 1
        return round(self.base_damage * (1.0 + UPGRADE_DAMAGE_PER_LEVEL * next_level), 2)

    def upgrade_cost(self):
        if self.at_max_upgrade or self.base_damage <= 0:
            return None
        rarity_multiplier = FORGE_RARITY_MULTIPLIERS.get(self.rarity, 1.0)
        cost = (FORGE_BASE_COST + int(self.base_damage * FORGE_DAMAGE_COST_MULTIPLIER) + self.upgrade_level * FORGE_TIER_COST) * rarity_multiplier
        return max(40, int(round(cost / 5.0) * 5))

    def upgrade_weapon(self):
        if self.at_max_upgrade or self.base_damage <= 0:
            return False
        self.upgrade_level += 1
        self.additional_damage = round(self.base_damage * (1.0 + UPGRADE_DAMAGE_PER_LEVEL * self.upgrade_level), 2)
        return True

    def to_dict(self):
        return {
            "item_name": self.item_name,
            "attributes": self.attributes,
            "additional_damage": self.additional_damage,
            "is_consumable": self.is_consumable,
            "heal_amount": self.heal_amount,
            "is_armor": self.is_armor,
            "defense_bonus": self.defense_bonus,
            "rarity": self.rarity,
            "upgrade_level": self.upgrade_level,
            "base_damage": self.base_damage,
            "quantity": self.quantity,
        }

    @classmethod
    def from_dict(cls, data):
        name = data["item_name"]
        current_damage = float(data["additional_damage"])
        base_damage = float(data.get("base_damage", KNOWN_BASE_DAMAGE.get(name, current_damage)))
        upgrade_level = data.get("upgrade_level")
        if upgrade_level is None:
            upgrade_level = 0
            if base_damage > 0 and current_damage > base_damage * 1.01:
                upgrade_level = max(1, int(round(math.log(current_damage / base_damage, 1.20))))
        return cls(
            name,
            data["attributes"],
            current_damage,
            data.get("is_consumable", False),
            data.get("heal_amount", 0),
            data.get("is_armor", False),
            data.get("defense_bonus", 0.0),
            data.get("rarity", KNOWN_RARITY.get(name, "Common")),
            upgrade_level,
            base_damage,
            data.get("quantity", 1),
        )
