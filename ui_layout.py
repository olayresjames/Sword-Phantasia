"""Resolution-aware layout contracts shared by fullscreen game surfaces."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LayoutMetrics:
    width: int
    height: int
    margin: int
    sidebar: int
    readable_width: int
    region_scene_height: int
    battle_deck_height: int


def layout_metrics(width, height):
    width, height = max(1024, int(width)), max(700, int(height))
    margin = max(18, min(42, width // 45))
    sidebar = max(205, min(260, width // 6))
    readable_width = max(620, min(1040, width - sidebar - margin * 4))
    region_scene_height = max(210, min(300, int(height * .29)))
    battle_deck_height = max(205, min(238, int(height * .285)))
    return LayoutMetrics(width, height, margin, sidebar, readable_width, region_scene_height, battle_deck_height)
