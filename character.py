import json
import os
import sys
import threading
from item import Item

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

try:
    import pygame
    pygame.mixer.init()
    def _level_up_sound():
        try:
            pygame.mixer.Sound(resource_path("assets/audio/level_up.mp3")).play()
        except (FileNotFoundError, pygame.error):
            pass
except ImportError:
    def _level_up_sound():
        pass

class Character:
    def __init__(self, name, level=1, starting_weapon=None):
        self.name = name
        self.level = level
        self.max_hp = 100 + (level - 1) * 20
        self.hp = self.max_hp
        self.mana = 100
        self.experience = 0
        self.coins = 0
        self.inventory = []
        self.equipped_weapon = None
        self.starting_weapon = starting_weapon
        self.equipped_armor = None
        self.current_region = "frontier"
        self.quest_progress = {}
        self.completed_quests = []

    def use_mana(self, amount):
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False

    def add_experience(self, exp):
        self.experience += exp
        # Level up for every 100 EXP gained
        while self.experience >= 100:
            self.experience -= 100
            self.level += 1
            self.max_hp += 20
            self.hp = self.max_hp  # Heal to full on level up
            _level_up_sound()

    def add_coins(self, amount):
        self.coins += amount
        
    def spend_coins(self, amount):
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False

    def save_to_file(self, filename="savegame.json"):
        data = {
            "save_version": 2,
            "name": self.name,
            "level": self.level,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "mana": self.mana,
            "experience": self.experience,
            "coins": self.coins,
            "inventory": [item.to_dict() for item in self.inventory],
            "starting_weapon": self.starting_weapon,
            "current_region": self.current_region,
            "quest_progress": self.quest_progress,
            "completed_quests": self.completed_quests,
            "equipped_weapon": self.equipped_weapon.to_dict() if self.equipped_weapon else None,
            "equipped_armor": getattr(self, 'equipped_armor').to_dict() if getattr(self, 'equipped_armor', None) else None
        }
        temp_filename = f"{filename}.tmp"
        with open(temp_filename, "w") as f:
            json.dump(data, f)
        os.replace(temp_filename, filename)

    @classmethod
    def load_from_file(cls, filename="savegame.json"):
        if not os.path.exists(filename):
            return None
        with open(filename, "r") as f:
            data = json.load(f)
        char = cls(data["name"], data["level"])
        char.max_hp = data.get("max_hp", 100 + (char.level - 1) * 20)
        char.hp = data.get("hp", char.max_hp)
        char.mana = data.get("mana", 100)
        char.experience = data.get("experience", 0)
        char.coins = data.get("coins", 0)
        char.current_region = data.get("current_region", "frontier")
        char.quest_progress = data.get("quest_progress", {})
        char.completed_quests = data.get("completed_quests", [])
        char.inventory = [Item.from_dict(item_data) for item_data in data.get("inventory", [])]
        equipped_data = data.get("equipped_weapon")
        if equipped_data:
            char.equipped_weapon = Item.from_dict(equipped_data)
        char.starting_weapon = data.get("starting_weapon")
        if not char.starting_weapon and char.equipped_weapon:
            # Older save files did not record the character's starting weapon.
            weapon_name = char.equipped_weapon.item_name.lower()
            char.starting_weapon = next(
                (weapon for weapon in ("Sword", "Bow", "Axe") if weapon.lower() in weapon_name),
                None
            )
        armor_data = data.get("equipped_armor")
        if armor_data:
            char.equipped_armor = Item.from_dict(armor_data)
        return char
