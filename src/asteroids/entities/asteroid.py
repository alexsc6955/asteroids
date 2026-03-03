"""
Asteroid entity for Asteroids gameplay.
"""

from __future__ import annotations

from mini_arcade_core.engine.entities import BaseEntity
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
        asteroid: Asteroid = Asteroid.from_dict(
            {
                "id": int(entity_id),
                "name": f"Asteroid {entity_id}",
                "transform": {
                    "center": {"x": pos.x, "y": pos.y},
                    "size": {"width": radius * 2.0, "height": radius * 2.0},
                    "rotation_deg": angle_deg,
                },
                "shape": {"kind": "poly"},
                "collider": {"kind": "circle", "radius": radius},
                "kinematic": {
                    "velocity": {"vx": vel.x, "vy": vel.y},
                    "acceleration": {"ax": 0.0, "ay": 0.0},
                    "max_speed": max(1.0, (vel.x * vel.x + vel.y * vel.y) ** 0.5),
                },
                "style": {"fill": (200, 210, 230, 255)},
            }
        )
        asteroid.radius = radius
        asteroid.size_level = size_level
        asteroid.spin_deg = spin_deg
        asteroid.points = points
        return asteroid
