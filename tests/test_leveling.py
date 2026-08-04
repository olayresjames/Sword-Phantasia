import unittest

from character import Character, experience_to_next_level


class LevelingTests(unittest.TestCase):
    def test_multiple_levels_and_hp_growth(self):
        hero = Character("Tester")
        hero.hp = 1
        hero.add_experience(250)
        self.assertEqual(hero.level, 3)
        self.assertEqual(hero.experience, 50)
        self.assertEqual(hero.max_hp, 140)
        self.assertEqual(hero.hp, hero.max_hp)

    def test_postgame_experience_curve_increases(self):
        self.assertEqual(experience_to_next_level(10), 100)
        self.assertEqual(experience_to_next_level(11), 125)
        self.assertEqual(experience_to_next_level(15), 225)


if __name__ == "__main__":
    unittest.main()
