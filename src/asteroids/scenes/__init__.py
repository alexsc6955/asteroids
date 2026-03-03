"""
Scene modules for Asteroids.
"""

from __future__ import annotations

from .asteroids import AsteroidsScene
from .menu import AsteroidsMenuScene
from .pause import AsteroidsPauseScene

__all__ = [
    "AsteroidsScene",
    "AsteroidsMenuScene",
    "AsteroidsPauseScene",
]
