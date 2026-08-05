"""Validate fullscreen layout contracts at the supported desktop sizes."""

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ui_layout import layout_metrics


SUPPORTED_RESOLUTIONS = ((1280, 720), (1366, 768), (1920, 1080), (2560, 1440))


def build_report():
    report = []
    for width, height in SUPPORTED_RESOLUTIONS:
        metrics = layout_metrics(width, height)
        checks = {
            "readable_content": metrics.readable_width >= 620,
            "sidebar_fits": metrics.sidebar + metrics.readable_width < width,
            "region_scene_fits": 210 <= metrics.region_scene_height <= int(height * .42),
            "battle_deck_fits": 205 <= metrics.battle_deck_height <= int(height * .34),
        }
        report.append({
            "resolution": f"{width}x{height}",
            "metrics": metrics.__dict__,
            "checks": checks,
            "passed": all(checks.values()),
        })
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, help="Optional path for a JSON report")
    args = parser.parse_args()
    report = build_report()
    output = json.dumps(report, indent=2)
    if args.out:
        args.out.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0 if all(entry["passed"] for entry in report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
