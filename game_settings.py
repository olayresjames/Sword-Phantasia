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
    "ui_scale": "100%",
    "color_vision": "Default",
    "high_contrast": False,
    "reduce_flashes": False,
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
        "ui_scale": source.get("ui_scale") if source.get("ui_scale") in ("100%", "115%", "130%") else "100%",
        "color_vision": source.get("color_vision") if source.get("color_vision") in ("Default", "Deuteranopia", "Tritanopia") else "Default",
        "high_contrast": bool(source.get("high_contrast", False)),
        "reduce_flashes": bool(source.get("reduce_flashes", False)),
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
    except (tk.TclError, AttributeError, NameError):
        try:
            window.state("zoomed")
        except Exception:
            width = window.winfo_screenwidth()
            height = window.winfo_screenheight()
            window.geometry(f"{width}x{height}+0+0")
    apply_accessibility(window)
    try:
        from input_manager import enable_controller_navigation
        enable_controller_navigation(window)
    except (ImportError, tk.TclError):
        pass
    try:
        from screen_manager import screen_manager
        screen_manager.register(window)
    except (ImportError, tk.TclError):
        pass


def apply_accessibility(window):
    factor = {"100%": 1.0, "115%": 1.15, "130%": 1.30}.get(settings.get("ui_scale"), 1.0)
    try:
        system_scale = max(1.0, window.winfo_fpixels("1i") / 72.0)
        window.tk.call("tk", "scaling", system_scale * factor)
    except (tk.TclError, TypeError, ValueError):
        pass


def accessible_color(role, fallback):
    palettes = {
        "Deuteranopia": {"danger": "#ff8c42", "success": "#55c7d9", "mana": "#6ba5ff", "special": "#d69cff"},
        "Tritanopia": {"danger": "#ef5b78", "success": "#62d49b", "mana": "#4fc3c8", "special": "#f0a6ca"},
    }
    if settings.get("high_contrast"):
        return {"danger": "#ff6b6b", "success": "#75f0b0", "mana": "#78c6ff", "special": "#e0b0ff"}.get(role, fallback)
    return palettes.get(settings.get("color_vision"), {}).get(role, fallback)


def apply_display_mode(window, mode=None):
    # Kept as the public entry point for existing callers. Sword Phantasia now
    # deliberately uses a seamless fullscreen presentation on every screen.
    apply_fullscreen(window)


settings = SettingsManager()
