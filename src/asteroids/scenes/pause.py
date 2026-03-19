"""
Pause overlay scene for Asteroids.
"""

from __future__ import annotations

from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem, MenuStyle

from asteroids.scenes.commands import (
    BackToMenuCommand,
    RestartAsteroidsCommand,
    ResumeAsteroidsCommand,
)


@register_scene("asteroids_pause")
class AsteroidsPauseScene(BaseMenuScene):
    """Pause scene."""

    @property
    def menu_title(self) -> str | None:
        return "PAUSED"

    def menu_style(self) -> MenuStyle:
        return MenuStyle(
            overlay_color=(0, 0, 0, 190),
            panel_color=(16, 18, 26, 238),
            button_enabled=True,
            button_fill=(10, 10, 16, 255),
            button_border=(80, 96, 126, 255),
            button_selected_border=(160, 220, 255, 255),
            normal=(220, 226, 240, 255),
            selected=(255, 255, 255, 255),
            hint="ENTER select  ESC resume  F1 debug  F12 record",
            hint_color=(160, 176, 196, 255),
        )

    def menu_items(self):
        return [
            MenuItem("continue", "CONTINUE", ResumeAsteroidsCommand),
            MenuItem("restart", "RESTART", RestartAsteroidsCommand),
            MenuItem("menu", "MAIN MENU", BackToMenuCommand),
        ]
