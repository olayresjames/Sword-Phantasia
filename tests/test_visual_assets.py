import unittest
from pathlib import Path

from battle_panel import MONSTER_SPRITES
from world_data import ASCENDED_MONSTERS, DEMON_KING, MINIBOSSES, REGIONS


class VisualAssetTests(unittest.TestCase):
    def test_every_enemy_has_a_unique_existing_sprite(self):
        enemies = []
        for region in REGIONS.values():
            enemies.extend(region.monsters)
        for variants in ASCENDED_MONSTERS.values():
            enemies.extend(variants)
        enemies.extend(MINIBOSSES.values())
        enemies.append(DEMON_KING)

        sprite_paths = []
        for enemy in enemies:
            self.assertIn(enemy.sprite_key, MONSTER_SPRITES, enemy.name)
            sprite_path = Path(MONSTER_SPRITES[enemy.sprite_key])
            self.assertTrue(sprite_path.is_file(), f"Missing sprite for {enemy.name}: {sprite_path}")
            sprite_paths.append(sprite_path.as_posix())

        self.assertEqual(len(sprite_paths), len(set(sprite_paths)), "Enemy sprites must not be reused")

    def test_final_boss_sprite_is_reserved_for_the_final_boss(self):
        boss_path = MONSTER_SPRITES[DEMON_KING.sprite_key]
        for region in REGIONS.values():
            for enemy in region.monsters:
                self.assertNotEqual(boss_path, MONSTER_SPRITES[enemy.sprite_key], enemy.name)


if __name__ == "__main__":
    unittest.main()
