import unittest

from game_data import difficulty_profile, scale_enemy_stats, scale_player_damage, scale_rewards


class CombatCalculationTests(unittest.TestCase):
    def test_easy_reduces_enemy_and_boosts_player(self):
        hp, attack = scale_enemy_stats(100, 20, "Easy")
        self.assertEqual((hp, attack), (80, 15))
        self.assertEqual(scale_player_damage(100, "Easy"), 115)

    def test_hard_increases_enemy_and_rewards(self):
        hp, attack = scale_enemy_stats(100, 20, "Hard")
        self.assertEqual((hp, attack), (130, 25))
        self.assertEqual(scale_player_damage(100, "Hard"), 90)
        self.assertEqual(scale_rewards(40, 20, "Hard"), (50, 25))

    def test_unknown_difficulty_is_normal(self):
        self.assertEqual(difficulty_profile("Impossible"), difficulty_profile("Normal"))


if __name__ == "__main__":
    unittest.main()
