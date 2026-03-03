"""
Models for Asteroids gameplay.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.sim_scene import BaseIntent, BaseTickContext, BaseWorld

from asteroids.entities import EntityId


@dataclass
class AsteroidsWorld(BaseWorld):
    """
    World state for Asteroids.
    """

    viewport: tuple[float, float]
    score: int = 0
    lives: int = 3
    level: int = 1
    game_over: bool = False

    def ship(self) -> BaseEntity | None:
        return self.get_entity_by_id(int(EntityId.SHIP))

    def asteroids(self) -> list[BaseEntity]:
        return self.get_entities_by_id_range(
            int(EntityId.ASTEROID_START),
            int(EntityId.ASTEROID_END),
        )

    def bullets(self) -> list[BaseEntity]:
        return self.get_entities_by_id_range(
            int(EntityId.BULLET_START),
            int(EntityId.BULLET_END),
        )


@dataclass(frozen=True)
class AsteroidsIntent(BaseIntent):
    """
    Player intent for one tick.
    """

    rotate_left: bool = False
    rotate_right: bool = False
    thrust: bool = False
    fire: bool = False
    pause: bool = False


@dataclass
class AsteroidsTickContext(
    BaseTickContext[AsteroidsWorld, AsteroidsIntent]
):
    """
    Tick context for Asteroids.
    """

