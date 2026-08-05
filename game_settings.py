"""Persistent, validated accessibility and control settings."""

import json
import os
import tkinter as tk

from game_data import DIFFICULTY_PROFILES, TEXT_SPEED_MULTIPLIERS


DEFAULT_KEYBINDINGS = {
    "walk_forward": "w",
    "walk_back": "s",
    "walk_left": "a",
    "walk_right": "d",
    "inventory": "i",
    "equip": "e",
    "region_map": "m",
    "quest_log": "q",
    "options": "Escape",
    "battle_attack": "a",
    "battle_defend": "d",
    "battle_item": "i",
    "battle_skill": "s",
    "battle_escape": "r",
}

DEFAULT_SETTINGS = {
    "difficulty": "Normal",
    "text_speed": "Normal",
    "music_volume": 0.65,
    "sfx_volume": 0.80,
    "display_mode": "Fullscreen",
    "reduce_animations": False,
    "keybindings": DEFAULT_KEYBINDINGS,
}


def _volume(value, fallback):
    try:
        return min(1.0, max(0.0, float(value)))
    except (TypeError, ValueError):
        return fallback


def validate_settings(data):
    source = data if isinstance(data, dict) else {}
    keys = source.get("keybindings", {})
    clean_keys = dict(DEFAULT_KEYBINDINGS)
    if isinstance(keys, dict):
        for action, default in DEFAULT_KEYBINDINGS.items():
            value = keys.get(action, default)
            if isinstance(value, str) and value.strip() and len(value.strip()) <= 12:
                clean_keys[action] = value.strip()
    return {
        "difficulty": source.get("difficulty") if source.get("difficulty") in DIFFICULTY_PROFILES else "Normal",
        "text_speed": source.get("text_speed") if source.get("text_speed") in TEXT_SPEED_MULTIPLIERS else "Normal",
        "music_volume": _volume(source.get("music_volume"), DEFAULT_SETTINGS["music_volume"]),
        "sfx_volume": _volume(source.get("sfx_volume"), DEFAULT_SETTINGS["sfx_volume"]),
        "display_mode": "Fullscreen",
        "reduce_animations": bool(source.get("reduce_animations", False)),
        "keybindings": clean_keys,
    }


class SettingsManager:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.values = dict(DEFAULT_SETTINGS)
        self.values["keybindings"] = dict(DEFAULT_KEYBINDINGS)
        self.load()

    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as handle:
                self.values = validate_settings(json.load(handle))
        except (OSError, ValueError, TypeError):
            self.values = validate_settings(self.values)
        return self.values

    def save(self, updates=None):
        if updates:
            merged = dict(self.values)
            merged.update(updates)
            self.values = validate_settings(merged)
        temporary = f"{self.filename}.tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(self.values, handle, indent=2)
        os.replace(temporary, self.filename)

    def get(self, key, default=None):
        return self.values.get(key, default)

    def key(self, action):
        return self.values["keybindings"].get(action, DEFAULT_KEYBINDINGS[action])

    def delay(self, milliseconds):
        if self.get("reduce_animations"):
            return max(1, min(90, int(milliseconds * 0.15)))
        return max(1, int(milliseconds * TEXT_SPEED_MULTIPLIERS[self.get("text_speed")]))


def key_sequence(key):
    return f"<KeyPress-{key}>"


def apply_fullscreen(window):
    """Use one borderless fullscreen presentation across every game surface."""
    try:
        window.attributes("-fullscreen", True)
        return
    except (tk.TclError, AttributeError, NameError):
        pass
    try:
        window.state("zoomed")
    except Exception:
        width = window.winfo_screenwidth()
        height = window.winfo_screenheight()
        window.geometry(f"{width}x{height}+0+0")


def apply_display_mode(window, mode=None):
    # Kept as the public entry point for existing callers. Sword Phantasia now
    # deliberately uses a seamless fullscreen presentation on every screen.
    apply_fullscreen(window)


settings = SettingsManager()
