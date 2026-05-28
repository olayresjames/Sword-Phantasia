class Item:
    def __init__(self, item_name, attributes, additional_damage, is_consumable=False, heal_amount=0, is_armor=False, defense_bonus=0.0):
        self.item_name = item_name
        self.attributes = attributes
        self.additional_damage = additional_damage
        self.is_consumable = is_consumable
        self.heal_amount = heal_amount
        self.is_armor = is_armor
        self.defense_bonus = defense_bonus

    def apply_upgrades(self, percentage):
        additional_bonus = (percentage / 100.0) * self.additional_damage
        self.additional_damage += additional_bonus
        print(f"Upgraded additional damage: {self.additional_damage}")

    def to_dict(self):
        return {
            "item_name": self.item_name,
            "attributes": self.attributes,
            "additional_damage": self.additional_damage,
            "is_consumable": self.is_consumable,
            "heal_amount": self.heal_amount,
            "is_armor": self.is_armor,
            "defense_bonus": self.defense_bonus
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["item_name"], data["attributes"], data["additional_damage"], data.get("is_consumable", False), data.get("heal_amount", 0), data.get("is_armor", False), data.get("defense_bonus", 0.0))