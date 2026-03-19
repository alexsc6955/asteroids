"""
System pipeline helpers for Asteroids scene setup.
"""

from __future__ import annotations

from asteroids.scenes.asteroids.systems import (
    AsteroidsWaveProgressionSystem,
    BulletSpawnSystem,
    CollisionSystem,
    ShipControlSystem,
    WorldMotionBundle,
)


def build_asteroids_systems() -> tuple[object, ...]:
    """
    Build the ordered gameplay systems for Asteroids.
    """
    return (
        ShipControlSystem(),
        BulletSpawnSystem(),
        WorldMotionBundle(),
        CollisionSystem(),
        AsteroidsWaveProgressionSystem(),
    )


__all__ = ["build_asteroids_systems"]
