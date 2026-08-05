import tempfile
import unittest
from pathlib import Path

from character import Character


class ProgressionPersistenceTests(unittest.TestCase):
    def test_tutorial_progress_survives_save_and_load(self):
        with tempfile.TemporaryDirectory() as folder:
            save_path = Path(folder) / "hero.json"
            hero = Character("Guide Tester")
            hero.tutorial_flags = ["movement", "exploration", "combat_intent"]
            hero.save_to_file(str(save_path))

            loaded = Character.load_from_file(str(save_path))
            self.assertEqual(loaded.tutorial_flags, hero.tutorial_flags)

    def test_old_saves_without_tutorial_progress_remain_compatible(self):
        hero = Character("Legacy Hero")
        data = hero.to_dict()
        data.pop("tutorial_flags")
        Character.validate_save_data(data)


if __name__ == "__main__":
    unittest.main()
