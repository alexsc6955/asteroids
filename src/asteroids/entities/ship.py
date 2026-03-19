"""
Ship entity for Asteroids gameplay.
"""

from __future__ import annotations

from typing import Any

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.entity_blueprints import build_entity_payload

from .entity_id import EntityId


class Ship(BaseEntity):
    """
    Player ship entity.
    """

    @staticmethod
    def build(*, x: float, y: float) -> "Ship":
        """Build the player ship at an explicit world position."""

        ship: Ship = Ship.from_dict(
            {
                "id": int(EntityId.SHIP),
                "name": "Ship",
                "transform": {
                    "center": {"x": x, "y": y},
                    "size": {"width": 24.0, "height": 28.0},
                    "rotation_deg": -90.0,
                },
                "shape": {"kind": "triangle"},
                "collider": {"kind": "circle", "radius": 12.0},
                "kinematic": {
                    "velocity": {"vx": 0.0, "vy": 0.0},
                    "acceleration": {"ax": 0.0, "ay": 0.0},
                    "max_speed": 330.0,
                },
                "style": {
                    "stroke": {
                        "color": (240, 240, 245, 255),
                        "thickness": 1.0,
                    },
                },
                "tags": ["ship", "player"],
            }
        )
        ship.ship_radius = 12.0
        ship.ship_thrusting = False
        ship.fire_cd = 0.0
        ship.respawn_timer = 0.0
        ship.invuln_timer = 0.0
        ship.thrust_color = (255, 150, 90, 255)
        return ship

    @staticmethod
    def build_from_template(
        *,
        template: dict[str, Any],
        viewport: tuple[float, float],
        overrides: dict[str, Any] | None = None,
    ) -> "Ship":
        """Build the player ship from a template plus runtime overrides."""

        payload = build_entity_payload(
            template,
            viewport=viewport,
            overrides={
                "id": int(EntityId.SHIP),
                "name": "Ship",
                **(overrides or {}),
            },
        )
        ship: Ship = Ship.from_dict(payload)
        ship.ship_radius = float(payload.get("ship_radius", 12.0))
        ship.ship_thrusting = False
        ship.fire_cd = 0.0
        ship.respawn_timer = 0.0
        ship.invuln_timer = 0.0
        ship.thrust_color = tuple(
            payload.get("thrust_color", (255, 150, 90, 255))
        )
        ship.tags = tuple(dict.fromkeys((*ship.tags, "ship", "player")))
        return ship
