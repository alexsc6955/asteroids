"""
Bootstrap helpers for Asteroids scene setup.
"""

from __future__ import annotations

from typing import Any

from mini_arcade_core.scenes.bootstrap import resolve_named_templates
from mini_arcade_core.spaces.math.vec2 import Vec2

from asteroids.entities import build_ship
from asteroids.scenes.asteroids.models import AsteroidsWorld
from asteroids.scenes.asteroids.spawn import (
    asteroid_wave_spawn_spec,
    spawn_initial_asteroid_wave,
)


def build_asteroids_world(
    *,
    viewport: tuple[float, float],
    entities_cfg: dict[str, Any],
) -> AsteroidsWorld:
    """
    Build the initial Asteroids world and opening wave.
    """
    templates = resolve_named_templates(
        entities_cfg.get("templates", {}) or {}
    )
    ship_template = templates.get("ship", {})
    ship = build_ship(template=ship_template, viewport=viewport)
    ship_pos = Vec2(ship.transform.center.x, ship.transform.center.y)
    wave_cfg = entities_cfg.get("wave", {}) or {}
    wave_spec = asteroid_wave_spawn_spec(wave_cfg)

    world = AsteroidsWorld(
        entities=[],
        viewport=viewport,
        score=0,
        lives=3,
        level=1,
        game_over=False,
        entity_templates=templates,
        wave_config=wave_cfg,
        wave_spawn_spec=wave_spec,
        ship_spawn_position=(ship_pos.x, ship_pos.y),
    )
    world.entities.append(ship)
    world.entities.extend(spawn_initial_asteroid_wave(world, wave_spec))
    return world


__all__ = ["build_asteroids_world"]
