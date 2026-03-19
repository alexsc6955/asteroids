"""
Asteroid entity for Asteroids gameplay.
"""

from __future__ import annotations

from typing import Any

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.entity_blueprints import build_entity_payload
from mini_arcade_core.spaces.math.vec2 import Vec2


class Asteroid(BaseEntity):
    """
    Gameplay asteroid entity.
    """

    @staticmethod
    def build(
        *,
        entity_id: int,
        pos: Vec2,
        vel: Vec2,
        radius: float,
        size_level: int,
        angle_deg: float,
        spin_deg: float,
        points: tuple[tuple[float, float], ...],
    ) -> "Asteroid":
        """Build an asteroid entity directly from concrete gameplay values."""

        asteroid: Asteroid = Asteroid.from_dict(
            {
                "id": int(entity_id),
                "name": f"Asteroid {entity_id}",
                "transform": {
                    "center": {"x": pos.x, "y": pos.y},
                    "size": {"width": radius * 2.0, "height": radius * 2.0},
                    "rotation_deg": angle_deg,
                },
                "shape": {
                    "kind": "poly",
                    "points": [
                        {"x": float(px), "y": float(py)} for px, py in points
                    ],
                },
                "collider": {"kind": "circle", "radius": radius},
                "kinematic": {
                    "velocity": {"vx": vel.x, "vy": vel.y},
                    "acceleration": {"ax": 0.0, "ay": 0.0},
                    "max_speed": max(
                        1.0, (vel.x * vel.x + vel.y * vel.y) ** 0.5
                    ),
                },
                "style": {
                    "stroke": {
                        "color": (200, 210, 230, 255),
                        "thickness": 1.0,
                    },
                },
                "tags": ["asteroid"],
            }
        )
        asteroid.radius = radius
        asteroid.size_level = size_level
        asteroid.spin_deg = spin_deg
        asteroid.points = points
        asteroid.tags = tuple(dict.fromkeys((*asteroid.tags, "asteroid")))
        return asteroid

    @staticmethod
    def build_from_template(
        *,
        template: dict[str, Any],
        viewport: tuple[float, float],
        entity_id: int,
        pos: Vec2,
        vel: Vec2,
        radius: float,
        size_level: int,
        angle_deg: float,
        spin_deg: float,
        points: tuple[tuple[float, float], ...],
    ) -> "Asteroid":
        """Build an asteroid entity from a template plus runtime overrides."""

        payload = build_entity_payload(
            template,
            viewport=viewport,
            overrides={
                "id": int(entity_id),
                "name": f"Asteroid {entity_id}",
                "transform": {
                    "position": {"x": pos.x, "y": pos.y},
                    "size": {"width": radius * 2.0, "height": radius * 2.0},
                    "rotation_deg": angle_deg,
                },
                "shape": {
                    "kind": "poly",
                    "points": [
                        {"x": float(px), "y": float(py)} for px, py in points
                    ],
                },
                "collider": {"kind": "circle", "radius": radius},
                "kinematic": {
                    "velocity": {"vx": vel.x, "vy": vel.y},
                    "acceleration": {"ax": 0.0, "ay": 0.0},
                    "max_speed": max(
                        1.0, (vel.x * vel.x + vel.y * vel.y) ** 0.5
                    ),
                },
            },
        )
        asteroid: Asteroid = Asteroid.from_dict(payload)
        asteroid.radius = radius
        asteroid.size_level = size_level
        asteroid.spin_deg = spin_deg
        asteroid.points = points
        asteroid.tags = tuple(dict.fromkeys((*asteroid.tags, "asteroid")))
        return asteroid
