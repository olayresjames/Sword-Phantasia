import json
import os
import shutil
import sys
from item import Item
from game_data import INVENTORY_SLOT_LIMIT, RARITY_SALVAGE
from audio_manager import audio_manager


def experience_to_next_level(level):
    """Keep the early game brisk, then slow postgame leveling gradually."""
    return 100 if level <= 10 else 100 + (level - 10) * 25

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def _level_up_sound():
    audio_manager.play_sound("level_up")

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
        self.defeated_minibosses = []
        self.materials = {}
        self.discovered_landmarks = []
        self.story_choices = []
        self.inventory_limit = INVENTORY_SLOT_LIMIT
        self.inventory_cleanup_summary = None
        self.loaded_from_backup = None

    @property
    def inventory_slots_used(self):
        return len(self.inventory)

    def consume_item(self, item):
        if item not in self.inventory or not item.is_consumable:
            return False
        if item.quantity > 1:
            item.quantity -= 1
        else:
            self.inventory.remove(item)
        return True

    def add_item(self, item, auto_salvage=True):
        """Stack supplies and recycle weak duplicate equipment into metal scrap."""
        if item.is_consumable:
            match = next((owned for owned in self.inventory if owned.stack_key() == item.stack_key()), None)
            if match:
                match.quantity += item.quantity
                return {"outcome": "stacked", "item": match, "quantity": item.quantity, "scrap": 0}

        if auto_salvage and not item.is_consumable:
            duplicates = [owned for owned in self.inventory if not owned.is_consumable and owned.item_name == item.item_name]
            if duplicates:
                strongest = max(duplicates, key=lambda owned: (owned.power_score(), owned.upgrade_level))
                if strongest.power_score() >= item.power_score():
                    scrap = RARITY_SALVAGE.get(item.rarity, 1)
                    self.materials["metal_scrap"] = self.materials.get("metal_scrap", 0) + scrap
                    return {"outcome": "salvaged", "item": strongest, "quantity": 0, "scrap": scrap}
                if self.equipped_weapon is strongest:
                    self.equipped_weapon = item
                if self.equipped_armor is strongest:
                    self.equipped_armor = item
                self.inventory.remove(strongest)
                scrap = RARITY_SALVAGE.get(strongest.rarity, 1)
                self.materials["metal_scrap"] = self.materials.get("metal_scrap", 0) + scrap

        if len(self.inventory) >= self.inventory_limit:
            if not item.is_consumable:
                scrap = RARITY_SALVAGE.get(item.rarity, 1)
                self.materials["metal_scrap"] = self.materials.get("metal_scrap", 0) + scrap
                return {"outcome": "salvaged", "item": None, "quantity": 0, "scrap": scrap}
            return {"outcome": "full", "item": None, "quantity": 0, "scrap": 0}

        self.inventory.append(item)
        return {"outcome": "added", "item": item, "quantity": item.quantity, "scrap": 0}

    def normalize_inventory(self):
        original = list(self.inventory)
        self.inventory = []
        stacked = salvaged = scrap = 0
        for item in original:
            result = self.add_item(item)
            stacked += item.quantity if result["outcome"] == "stacked" else 0
            salvaged += 1 if result["outcome"] == "salvaged" else 0
            scrap += result["scrap"]
        if stacked or salvaged:
            self.inventory_cleanup_summary = {"stacked": stacked, "salvaged": salvaged, "scrap": scrap}
        return self.inventory_cleanup_summary

    def use_mana(self, amount):
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False

    def add_experience(self, exp):
        self.experience += exp
        while self.experience >= experience_to_next_level(self.level):
            self.experience -= experience_to_next_level(self.level)
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
        data = self.to_dict()
        temp_filename = f"{filename}.tmp"
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as existing:
                    self.validate_save_data(json.load(existing))
                backup = f"{filename}.bak"
                older_backup = f"{filename}.bak2"
                if os.path.exists(backup):
                    shutil.copy2(backup, older_backup)
                shutil.copy2(filename, backup)
            except (OSError, ValueError, TypeError, KeyError):
                pass
        with open(temp_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_filename, filename)

    def to_dict(self):
        return {
            "save_version": 5,
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
            "defeated_minibosses": self.defeated_minibosses,
            "materials": self.materials,
            "discovered_landmarks": self.discovered_landmarks,
            "story_choices": self.story_choices,
            "equipped_weapon": self.equipped_weapon.to_dict() if self.equipped_weapon else None,
            "equipped_armor": getattr(self, 'equipped_armor').to_dict() if getattr(self, 'equipped_armor', None) else None
        }

    @staticmethod
    def validate_save_data(data):
        if not isinstance(data, dict):
            raise ValueError("Save data must be a JSON object.")
        if not isinstance(data.get("name"), str) or not data["name"].strip():
            raise ValueError("Save data has no valid character name.")
        level = data.get("level")
        if not isinstance(level, int) or isinstance(level, bool) or not 1 <= level <= 999:
            raise ValueError("Save data has an invalid level.")
        if not isinstance(data.get("inventory", []), list):
            raise ValueError("Save inventory must be a list.")
        for item in data.get("inventory", []):
            if not isinstance(item, dict) or not isinstance(item.get("item_name"), str) or not isinstance(item.get("attributes"), str):
                raise ValueError("Save inventory contains an invalid item.")
            if not isinstance(item.get("additional_damage", 0), (int, float)):
                raise ValueError("Save inventory contains invalid item stats.")
        for field in ("hp", "max_hp", "mana", "experience", "coins"):
            value = data.get(field, 0)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"Save field {field} must be numeric.")
        return data

    @classmethod
    def load_from_file(cls, filename="savegame.json"):
        data = None
        loaded_path = None
        last_error = None
        for candidate in (filename, f"{filename}.bak", f"{filename}.bak2"):
            if not os.path.exists(candidate):
                continue
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    candidate_data = json.load(f)
                cls.validate_save_data(candidate_data)
                data = candidate_data
                loaded_path = candidate
                break
            except (OSError, ValueError, TypeError, KeyError) as exc:
                last_error = exc
        if data is None:
            if last_error:
                raise ValueError(f"No valid save or backup could be loaded: {last_error}")
            return None
        char = cls(data["name"], data["level"])
        char.max_hp = max(1, int(data.get("max_hp", 100 + (char.level - 1) * 20)))
        char.hp = max(0, min(char.max_hp, int(data.get("hp", char.max_hp))))
        char.mana = max(0, min(100, int(data.get("mana", 100))))
        char.experience = max(0, int(data.get("experience", 0)))
        char.coins = max(0, int(data.get("coins", 0)))
        char.current_region = data.get("current_region", "frontier")
        char.quest_progress = data.get("quest_progress", {})
        char.completed_quests = data.get("completed_quests", [])
        char.defeated_minibosses = data.get("defeated_minibosses", [])
        char.materials = data.get("materials", {})
        char.discovered_landmarks = data.get("discovered_landmarks", [])
        char.story_choices = data.get("story_choices", [])
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
        char.loaded_from_backup = loaded_path if loaded_path != filename else None
        char.normalize_inventory()
        if char.equipped_weapon:
            owned = next((item for item in char.inventory if not item.is_armor and item.item_name == char.equipped_weapon.item_name and item.additional_damage == char.equipped_weapon.additional_damage), None)
            if owned:
                char.equipped_weapon = owned
        if char.equipped_armor:
            owned = next((item for item in char.inventory if item.is_armor and item.item_name == char.equipped_armor.item_name and item.defense_bonus == char.equipped_armor.defense_bonus), None)
            if owned:
                char.equipped_armor = owned
        return char
