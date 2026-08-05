import unittest

from game_settings import DEFAULT_KEYBINDINGS, validate_settings


class AccessibilitySettingsTests(unittest.TestCase):
    def test_accessibility_preferences_are_preserved(self):
        settings = validate_settings({
            "ui_scale": "130%",
            "color_vision": "Deuteranopia",
            "high_contrast": True,
            "reduce_flashes": True,
            "reduce_animations": True,
        })
        self.assertEqual(settings["ui_scale"], "130%")
        self.assertEqual(settings["color_vision"], "Deuteranopia")
        self.assertTrue(settings["high_contrast"])
        self.assertTrue(settings["reduce_flashes"])
        self.assertTrue(settings["reduce_animations"])

    def test_invalid_accessibility_values_fall_back_safely(self):
        settings = validate_settings({"ui_scale": "huge", "color_vision": "unknown"})
        self.assertEqual(settings["ui_scale"], "100%")
        self.assertEqual(settings["color_vision"], "Default")
        self.assertEqual(settings["keybindings"], DEFAULT_KEYBINDINGS)


if __name__ == "__main__":
    unittest.main()
