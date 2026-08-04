import unittest

from character import Character
from quests import QUESTS, record_event


class QuestTests(unittest.TestCase):
    def test_quest_catalog_has_varied_objectives(self):
        objective_types = {quest.objective_type for quest in QUESTS}
        self.assertTrue({"defeat", "collect", "landmark", "survive", "choice", "special_defeat"}.issubset(objective_types))

    def test_landmark_quest_completes_once(self):
        hero = Character("Scout")
        updates, completions = record_event(hero, "landmark", "old_watchtower")
        self.assertEqual(len(updates), 1)
        self.assertEqual(len(completions), 1)
        first_gold = hero.coins
        record_event(hero, "landmark", "old_watchtower")
        self.assertEqual(hero.coins, first_gold)


if __name__ == "__main__":
    unittest.main()
