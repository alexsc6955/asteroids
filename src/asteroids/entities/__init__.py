"""
Entities package for Asteroids gameplay.
"""

from __future__ import annotations

from mini_arcade_core.spaces.math.vec2 import Vec2

from .asteroid import Asteroid
from .bullet import Bullet
from .entity_id import EntityId
from .ship import Ship


def build_ship(*, x: float, y: float) -> Ship:
    return Ship.build(x=x, y=y)


def build_asteroid(
    *,
    entity_id: int,
    pos: Vec2,
    vel: Vec2,
    radius: float,
    size_level: int,
    angle_deg: float,
    spin_deg: float,
    points: tuple[tuple[float, float], ...],
) -> Asteroid:
    return Asteroid.build(
        entity_id=entity_id,
        pos=pos,
        vel=vel,
        radius=radius,
        size_level=size_level,
        angle_deg=angle_deg,
        spin_deg=spin_deg,
        points=points,
    )


def build_bullet(
    *,
    entity_id: int,
    pos: Vec2,
    vel: Vec2,
    ttl: float = 1.1,
    radius: float = 2.5,
) -> Bullet:
    return Bullet.build(
        entity_id=entity_id,
        pos=pos,
        vel=vel,
        ttl=ttl,
        radius=radius,
    )


__all__ = [
    "EntityId",
    "Ship",
    "Asteroid",
    "Bullet",
    "build_ship",
    "build_asteroid",
    "build_bullet",
]
