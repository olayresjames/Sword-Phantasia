import unittest

from ui_layout import layout_metrics
from tools.check_visual_layouts import build_report


class ResponsiveLayoutTests(unittest.TestCase):
    def test_supported_resolutions_keep_readable_content(self):
        for width, height in ((1280, 720), (1366, 768), (1920, 1080), (2560, 1440)):
            with self.subTest(resolution=(width, height)):
                metrics = layout_metrics(width, height)
                self.assertGreaterEqual(metrics.readable_width, 620)
                self.assertLess(metrics.sidebar + metrics.readable_width, width)
                self.assertGreaterEqual(metrics.region_scene_height, 210)
                self.assertLessEqual(metrics.battle_deck_height, int(height * .34))

    def test_small_inputs_are_clamped_to_supported_minimum(self):
        metrics = layout_metrics(800, 600)
        self.assertEqual((metrics.width, metrics.height), (1024, 700))

    def test_visual_layout_report_passes_every_supported_resolution(self):
        report = build_report()
        self.assertTrue(report)
        self.assertTrue(all(entry["passed"] for entry in report), report)


if __name__ == "__main__":
    unittest.main()
