"""
Ship entity for Asteroids gameplay.
"""

from __future__ import annotations

from mini_arcade_core.engine.entities import BaseEntity

from .entity_id import EntityId


class Ship(BaseEntity):
    """
    Player ship entity.
    """

    @staticmethod
    def build(*, x: float, y: float) -> "Ship":
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
                "style": {"fill": (240, 240, 245, 255)},
            }
        )
        ship.ship_radius = 12.0
        ship.ship_thrusting = False
        ship.fire_cd = 0.0
        ship.respawn_timer = 0.0
        ship.invuln_timer = 0.0
        return ship
