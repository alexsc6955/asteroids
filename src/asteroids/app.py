"""
Main application entrypoint for Asteroids.
"""

from __future__ import annotations

from mini_arcade_core import GameConfig, SceneRegistry, run_game
from mini_arcade_core.utils import logger
from mini_arcade_pygame_backend import PygameBackend, PygameBackendSettings

from asteroids.constants import FPS, WINDOW_SIZE


def run():
    """
    Discover scenes and launch the Asteroids game.
    """
    scene_registry = SceneRegistry(_factories={}).discover(
        "asteroids.scenes", "mini_arcade_core.scenes"
    )

    w_width, w_height = WINDOW_SIZE
    settings_data = {
        "window": {
            "width": w_width,
            "height": w_height,
            "title": "Asteroids (Pygame + mini-arcade-core)",
            "high_dpi": False,
            "resizable": True,
        },
        "renderer": {"background_color": (8, 10, 16)},
        "audio": {"enable": False},
    }
    backend_settings = PygameBackendSettings.from_dict(settings_data)
    backend = PygameBackend(settings=backend_settings)

    game_config = GameConfig(
        initial_scene="asteroids_menu",
        fps=FPS,
        backend=backend,
        virtual_resolution=WINDOW_SIZE,
    )
    logger.info("Starting Asteroids...")
    run_game(game_config=game_config, scene_registry=scene_registry)


if __name__ == "__main__":
    run()
