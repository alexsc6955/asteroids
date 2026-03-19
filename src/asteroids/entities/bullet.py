"""
Bullet entity for Asteroids gameplay.
"""

from __future__ import annotations

from typing import Any

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.entity_blueprints import build_entity_payload
from mini_arcade_core.spaces.math.vec2 import Vec2


class Bullet(BaseEntity):
    """
    Gameplay bullet entity.
    """

    @staticmethod
    def build(
        *,
        entity_id: int,
        pos: Vec2,
        vel: Vec2,
        ttl: float = 1.1,
        radius: float = 2.5,
    ) -> "Bullet":
        """Build a bullet entity directly from concrete gameplay values."""

        bullet: Bullet = Bullet.from_dict(
            {
                "id": int(entity_id),
                "name": f"Bullet {entity_id}",
                "transform": {
                    "center": {"x": pos.x, "y": pos.y},
                    "size": {"width": radius * 2.0, "height": radius * 2.0},
                },
                "shape": {"kind": "rect"},
                "collider": {"kind": "circle", "radius": radius},
                "kinematic": {
                    "velocity": {"vx": vel.x, "vy": vel.y},
                    "acceleration": {"ax": 0.0, "ay": 0.0},
                    "max_speed": max(
                        1.0, (vel.x * vel.x + vel.y * vel.y) ** 0.5
                    ),
                },
                "style": {"fill": (255, 255, 255, 255)},
                "life": {"ttl": ttl, "alive": True},
                "tags": ["bullet"],
            }
        )
        bullet.radius = radius
        return bullet

    @staticmethod
    def build_from_template(
        *,
        template: dict[str, Any],
        viewport: tuple[float, float],
        entity_id: int,
        pos: Vec2,
        vel: Vec2,
        ttl: float = 1.1,
        radius: float = 2.5,
    ) -> "Bullet":
        """Build a bullet entity from a template plus runtime overrides."""

        payload = build_entity_payload(
            template,
            viewport=viewport,
            overrides={
                "id": int(entity_id),
                "name": f"Bullet {entity_id}",
                "transform": {
                    "position": {"x": pos.x, "y": pos.y},
                    "size": {
                        "width": radius * 2.0,
                        "height": radius * 2.0,
                    },
                },
                "collider": {"kind": "circle", "radius": radius},
                "kinematic": {
                    "velocity": {"vx": vel.x, "vy": vel.y},
                    "acceleration": {"ax": 0.0, "ay": 0.0},
                    "max_speed": max(
                        1.0, (vel.x * vel.x + vel.y * vel.y) ** 0.5
                    ),
                },
                "life": {"ttl": ttl, "alive": True},
            },
        )
        bullet: Bullet = Bullet.from_dict(payload)
        bullet.radius = radius
        bullet.tags = tuple(dict.fromkeys((*bullet.tags, "bullet")))
        return bullet
