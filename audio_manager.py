"""Small, failure-tolerant audio service shared by every game screen."""

import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class AudioManager:
    SOUND_FILES = {
        "attack": "assets/audio/attack.mp3",
        "skill": "assets/audio/skill.mp3",
        "damage": "assets/audio/damage.mp3",
        "level_up": "assets/audio/level_up.mp3",
        "ui_select": "assets/audio/ui_select.wav",
        "victory": "assets/audio/victory.wav",
    }
    MUSIC_FILES = {
        "battle": "assets/audio/bgm_battle.mp3",
        "menu": "assets/audio/bgm_menu.wav",
        "region_frontier": "assets/audio/amb_frontier.wav",
        "region_mosswood": "assets/audio/amb_mosswood.wav",
        "region_crypt": "assets/audio/amb_crypt.wav",
        "region_throne": "assets/audio/amb_throne.wav",
    }

    def __init__(self):
        self.available = False
        self._pygame = None
        self._sounds = {}
        self.music_volume = 0.65
        self.sfx_volume = 0.80
        try:
            import pygame
            self._pygame = pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.available = True
        except (ImportError, OSError, RuntimeError):
            self.available = False

    def configure(self, music_volume=None, sfx_volume=None):
        if music_volume is not None:
            self.music_volume = min(1.0, max(0.0, float(music_volume)))
        if sfx_volume is not None:
            self.sfx_volume = min(1.0, max(0.0, float(sfx_volume)))
        if self.available:
            self._pygame.mixer.music.set_volume(self.music_volume)
            for sound in self._sounds.values():
                sound.set_volume(self.sfx_volume)

    def play_sound(self, name):
        if not self.available or name not in self.SOUND_FILES:
            return False
        try:
            sound = self._sounds.get(name)
            if sound is None:
                sound = self._pygame.mixer.Sound(resource_path(self.SOUND_FILES[name]))
                self._sounds[name] = sound
            sound.set_volume(self.sfx_volume)
            sound.play()
            return True
        except (OSError, self._pygame.error):
            return False

    def play_music(self, name="battle", loop=-1):
        if not self.available or name not in self.MUSIC_FILES:
            return False
        try:
            self._pygame.mixer.music.load(resource_path(self.MUSIC_FILES[name]))
            self._pygame.mixer.music.set_volume(self.music_volume)
            self._pygame.mixer.music.play(loop)
            return True
        except (OSError, self._pygame.error):
            return False

    def stop_music(self):
        if self.available:
            try:
                self._pygame.mixer.music.stop()
            except self._pygame.error:
                pass


audio_manager = AudioManager()
