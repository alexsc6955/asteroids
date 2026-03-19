"""
Models for Asteroids gameplay.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.sim_scene import (
    BaseIntent,
    BaseTickContext,
    BaseWorld,
    EntityIdDomain,
)

from asteroids.entities.entity_id import EntityId

if TYPE_CHECKING:
    from asteroids.scenes.asteroids.spawn import AsteroidWaveSpawnSpec


@dataclass
class AsteroidsWorld(BaseWorld):
    """
    World state for Asteroids.
    """

    entity_id_domains = {
        "ship": EntityIdDomain(
            start_id=int(EntityId.SHIP), end_id=int(EntityId.SHIP)
        ),
        "asteroid": EntityIdDomain(
            start_id=int(EntityId.ASTEROID_START),
            end_id=int(EntityId.ASTEROID_END),
        ),
        "bullet": EntityIdDomain(
            start_id=int(EntityId.BULLET_START),
            end_id=int(EntityId.BULLET_END),
        ),
    }
    viewport: tuple[float, float]
    score: int = 0
    lives: int = 3
    level: int = 1
    game_over: bool = False
    entity_templates: dict[str, dict[str, Any]] = field(default_factory=dict)
    wave_config: dict[str, Any] = field(default_factory=dict)
    wave_spawn_spec: AsteroidWaveSpawnSpec | None = None
    ship_spawn_position: tuple[float, float] = (0.0, 0.0)

    def ship(self) -> BaseEntity | None:
        """Return the current ship entity, if one is alive in the world."""

        ship = self.find_entity(tag="ship")
        if ship is not None:
            return ship
        entities = self.get_entities_in_domain("ship")
        return entities[0] if entities else None

    def asteroids(self) -> list[BaseEntity]:
        """Return all active asteroid entities."""

        asteroids = self.get_entities_by_tag("asteroid")
        if asteroids:
            return asteroids
        return self.get_entities_in_domain("asteroid")

    def bullets(self) -> list[BaseEntity]:
        """Return all active bullet entities."""

        bullets = self.get_entities_by_tag("bullet")
        if bullets:
            return bullets
        return self.get_entities_in_domain("bullet")


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
class AsteroidsTickContext(BaseTickContext[AsteroidsWorld, AsteroidsIntent]):
    """
    Tick context for Asteroids.
    """
