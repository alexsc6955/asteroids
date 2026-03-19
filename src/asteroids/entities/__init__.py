"""
Entities package for Asteroids gameplay.
"""

from __future__ import annotations

from typing import Any

from mini_arcade_core.spaces.math.vec2 import Vec2

from .asteroid import Asteroid
from .bullet import Bullet
from .entity_id import EntityId
from .ship import Ship


def build_ship(
    *,
    x: float | None = None,
    y: float | None = None,
    template: dict[str, Any] | None = None,
    viewport=None,
) -> Ship:
    """Build the ship from either explicit coordinates or a template."""

    if template is not None and viewport is not None:
        overrides = None
        if x is not None and y is not None:
            overrides = {"transform": {"position": {"x": x, "y": y}}}
        return Ship.build_from_template(
            template=template,
            viewport=viewport,
            overrides=overrides,
        )
    if x is None or y is None:
        raise ValueError(
            "x and y are required when no ship template is provided"
        )
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
    template: dict[str, Any] | None = None,
    viewport: tuple[float, float] | None = None,
) -> Asteroid:
    """Build an asteroid from either direct values or a template override."""

    if template is not None and viewport is not None:
        return Asteroid.build_from_template(
            template=template,
            viewport=viewport,
            entity_id=entity_id,
            pos=pos,
            vel=vel,
            radius=radius,
            size_level=size_level,
            angle_deg=angle_deg,
            spin_deg=spin_deg,
            points=points,
        )
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
    template: dict[str, Any] | None = None,
    viewport: tuple[float, float] | None = None,
) -> Bullet:
    """Build a bullet from either direct values or a template override."""

    if template is not None and viewport is not None:
        return Bullet.build_from_template(
            template=template,
            viewport=viewport,
            entity_id=entity_id,
            pos=pos,
            vel=vel,
            ttl=ttl,
            radius=radius,
        )
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
