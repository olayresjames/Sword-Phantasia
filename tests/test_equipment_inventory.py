import json
import os
import tempfile
import unittest

from character import Character
from item import Item, MAX_UPGRADE_LEVEL


class EquipmentInventoryTests(unittest.TestCase):
    def test_consumables_stack_and_consume_one(self):
        hero = Character("Alchemist")
        hero.add_item(Item("Potion", "Restorative", 0, is_consumable=True, heal_amount=25))
        hero.add_item(Item("Potion", "Restorative", 0, is_consumable=True, heal_amount=25, quantity=2))
        self.assertEqual(len(hero.inventory), 1)
        self.assertEqual(hero.inventory[0].quantity, 3)
        hero.consume_item(hero.inventory[0])
        self.assertEqual(hero.inventory[0].quantity, 2)

    def test_weak_duplicate_becomes_scrap(self):
        hero = Character("Smith")
        hero.add_item(Item("Bone Club", "Crude", 11))
        result = hero.add_item(Item("Bone Club", "Crude", 10))
        self.assertEqual(result["outcome"], "salvaged")
        self.assertEqual(hero.materials["metal_scrap"], 1)
        self.assertEqual(len(hero.inventory), 1)

    def test_forge_has_linear_cap(self):
        weapon = Item("Iron Sword", "Sturdy", 15)
        costs = []
        for _ in range(MAX_UPGRADE_LEVEL):
            costs.append(weapon.upgrade_cost())
            self.assertTrue(weapon.upgrade_weapon())
        self.assertTrue(all(later > earlier for earlier, later in zip(costs, costs[1:])))
        self.assertTrue(weapon.at_max_upgrade)
        self.assertFalse(weapon.upgrade_weapon())

    def test_save_backup_and_recovery(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "save.json")
            hero = Character("Backup Hero")
            hero.coins = 10
            hero.save_to_file(path)
            hero.coins = 25
            hero.save_to_file(path)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("not json")
            recovered = Character.load_from_file(path)
            self.assertEqual(recovered.coins, 10)
            self.assertEqual(recovered.loaded_from_backup, f"{path}.bak")

    def test_save_validation_rejects_invalid_level(self):
        with self.assertRaises(ValueError):
            Character.validate_save_data({"name": "Hero", "level": 0, "inventory": []})


if __name__ == "__main__":
    unittest.main()
