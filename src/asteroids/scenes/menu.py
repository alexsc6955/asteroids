"""
Main menu scene for Asteroids.
"""

from __future__ import annotations

from mini_arcade_core.engine.commands import QuitCommand
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem, MenuStyle

from asteroids.scenes.commands import StartAsteroidsCommand


@register_scene("asteroids_menu")
class AsteroidsMenuScene(BaseMenuScene):
    """Main menu scene."""

    @property
    def menu_title(self) -> str | None:
        return "ASTEROIDS"

    def menu_style(self) -> MenuStyle:
        return MenuStyle(
            background_color=(6, 8, 14, 255),
            panel_color=(16, 20, 34, 235),
            button_enabled=True,
            button_fill=(10, 12, 20, 255),
            button_border=(90, 110, 150, 255),
            button_selected_border=(160, 220, 255, 255),
            normal=(220, 226, 240, 255),
            selected=(255, 255, 255, 255),
            hint="ENTER start  ESC quit  F1 debug  F12 record",
            hint_color=(160, 176, 196, 255),
        )

    def menu_items(self):
        return [
            MenuItem("start", "START GAME", StartAsteroidsCommand),
            MenuItem("quit", "QUIT", QuitCommand),
        ]
