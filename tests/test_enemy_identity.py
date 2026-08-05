import unittest
from unittest.mock import patch

from world_data import ENEMY_SIGNATURE_INTENTS, choose_enemy_intent


class EnemyIdentityTests(unittest.TestCase):
    def test_signature_enemies_have_distinct_mechanics(self):
        abyss_moves = ENEMY_SIGNATURE_INTENTS["Abyss Stalker"]
        knight_moves = ENEMY_SIGNATURE_INTENTS["Hellfire Knight"]
        herald_moves = ENEMY_SIGNATURE_INTENTS["Void Herald"]

        self.assertTrue(any(move.hits > 1 for move in abyss_moves))
        self.assertTrue(any(move.mana_damage > 0 for move in knight_moves))
        self.assertTrue(any(move.hits > 1 and move.mana_damage > 0 for move in herald_moves))

    def test_named_enemy_uses_only_its_signature_pool(self):
        expected = ENEMY_SIGNATURE_INTENTS["Crypt Archer"][0]
        with patch("world_data.random.choices", return_value=[expected]) as choices:
            selected = choose_enemy_intent("skeleton", monster_name="Crypt Archer")
        self.assertIs(selected, expected)
        self.assertEqual(tuple(choices.call_args.args[0]), ENEMY_SIGNATURE_INTENTS["Crypt Archer"])

    def test_low_health_named_demon_keeps_valid_signature_weights(self):
        expected = ENEMY_SIGNATURE_INTENTS["Hellfire Knight"][0]
        with patch("world_data.random.choices", return_value=[expected]) as choices:
            choose_enemy_intent("demon", hp_ratio=.2, monster_name="Hellfire Knight")
        population = choices.call_args.args[0]
        weights = choices.call_args.kwargs["weights"]
        self.assertEqual(len(population), len(weights))


if __name__ == "__main__":
    unittest.main()
