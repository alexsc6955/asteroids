"""
Entity IDs for Asteroids gameplay.
"""

from __future__ import annotations

from enum import IntEnum


class EntityId(IntEnum):
    SHIP = 1
    ASTEROID_START = 100
    ASTEROID_END = 899
    BULLET_START = 900
    BULLET_END = 1499
