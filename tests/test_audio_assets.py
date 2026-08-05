import unittest
from pathlib import Path

from audio_manager import AudioManager


class OfflineAudioAssetTests(unittest.TestCase):
    def test_new_offline_audio_assets_exist(self):
        names = ("menu", "region_frontier", "region_mosswood", "region_crypt", "region_throne")
        for name in names:
            with self.subTest(name=name):
                path = Path(AudioManager.MUSIC_FILES[name])
                self.assertTrue(path.is_file(), path)
                self.assertEqual(path.suffix, ".wav")

        for name in ("ui_select", "victory"):
            with self.subTest(name=name):
                self.assertTrue(Path(AudioManager.SOUND_FILES[name]).is_file())


if __name__ == "__main__":
    unittest.main()
