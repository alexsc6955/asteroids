"""
Systems for Asteroids gameplay.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Iterable

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.systems import SystemBundle
from mini_arcade_core.scenes.systems.builtins import (
    KinematicMotionSystem,
    MotionBinding,
    ProjectileLifecycleBinding,
    ProjectileLifecycleBundle,
    SpawnBinding,
    SpawnSystem,
    ViewportConstraintBinding,
    ViewportConstraintSystem,
    WaveProgressionBinding,
    WaveProgressionSystem,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase
from mini_arcade_core.spaces.math.vec2 import Vec2

from asteroids.entities import build_asteroid, build_bullet
from asteroids.scenes.asteroids.models import (
    AsteroidsTickContext,
    AsteroidsWorld,
)
from asteroids.scenes.asteroids.spawn import (
    make_asteroid_points,
    resolve_wave_spawn_spec,
    spawn_asteroid_wave,
)
from asteroids.scenes.asteroids.systems.render import AsteroidsRenderSystem

__all__ = [
    "ShipControlSystem",
    "BulletSpawnSystem",
    "WorldMotionBundle",
    "MotionSystem",
    "CollisionSystem",
    "AsteroidsWaveProgressionSystem",
    "AsteroidsRenderSystem",
]


def _distance2(a: Vec2, b: Vec2) -> float:
    dx = a.x - b.x
    dy = a.y - b.y
    return dx * dx + dy * dy


def _dir_from_angle(angle_deg: float) -> Vec2:
    # Ship mesh points "up" when angle is 0, so gameplay forward is angle-90.
    rad = math.radians(angle_deg - 90.0)
    return Vec2(math.cos(rad), math.sin(rad))


def _ship(world: AsteroidsWorld) -> BaseEntity | None:
    return world.ship()


def _asteroids(world: AsteroidsWorld) -> list[BaseEntity]:
    return world.asteroids()


def _bullets(world: AsteroidsWorld) -> list[BaseEntity]:
    return world.bullets()


@dataclass
class ShipControlSystem:
    """
    Rotate/thrust the ship from player intent.
    """

    name: str = "asteroids_ship_control"
    phase: int = SystemPhase.CONTROL
    order: int = 20

    turn_speed_deg: float = 240.0
    thrust_accel: float = 280.0
    max_speed: float = 330.0

    def step(self, ctx: AsteroidsTickContext):
        """Apply rotation and thrust intent to the player ship."""

        world = ctx.world
        ship = _ship(world)
        intent = ctx.intent
        if ship is None or ship.kinematic is None:
            return
        if intent is None or world.game_over:
            ship.ship_thrusting = False
            return

        if float(getattr(ship, "respawn_timer", 0.0)) > 0.0:
            ship.ship_thrusting = False
            return

        if intent.rotate_left:
            ship.rotation_deg -= self.turn_speed_deg * ctx.dt
        if intent.rotate_right:
            ship.rotation_deg += self.turn_speed_deg * ctx.dt

        ship.ship_thrusting = bool(intent.thrust)
        if intent.thrust:
            d = _dir_from_angle(float(ship.rotation_deg))
            ship.kinematic.velocity.x += d.x * self.thrust_accel * ctx.dt
            ship.kinematic.velocity.y += d.y * self.thrust_accel * ctx.dt

        speed = math.hypot(
            ship.kinematic.velocity.x, ship.kinematic.velocity.y
        )
        if speed > self.max_speed and speed > 0.0:
            scale = self.max_speed / speed
            ship.kinematic.velocity.x *= scale
            ship.kinematic.velocity.y *= scale


@dataclass
class BulletSpawnSystem:
    """
    Spawn ship bullets when fire intent is triggered.
    """

    name: str = "asteroids_bullet_spawn"
    phase: int = SystemPhase.CONTROL
    order: int = 21

    fire_cooldown: float = 0.18
    bullet_speed: float = 460.0
    _spawn: SpawnSystem[AsteroidsTickContext] = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self._spawn = SpawnSystem(
            name=self.name,
            phase=self.phase,
            order=self.order,
            bindings=(
                SpawnBinding(
                    should_spawn=self._should_spawn,
                    spawn=self._spawn_bullet,
                    on_spawned=self._after_spawn,
                ),
            ),
        )

    @staticmethod
    def _should_spawn(ctx: AsteroidsTickContext) -> bool:
        ship = _ship(ctx.world)
        intent = ctx.intent
        return bool(
            ship is not None
            and ship.kinematic is not None
            and intent is not None
            and not ctx.world.game_over
            and intent.fire
            and float(getattr(ship, "respawn_timer", 0.0)) <= 0.0
            and float(getattr(ship, "fire_cd", 0.0)) <= 0.0
        )

    def _spawn_bullet(
        self,
        ctx: AsteroidsTickContext,
    ) -> BaseEntity | None:
        world = ctx.world
        ship = _ship(world)
        if ship is None or ship.kinematic is None:
            return None

        bullet_id = world.allocate_entity_id_for("bullet")
        if bullet_id is None:
            return None

        sx, sy = ship.transform.center.to_tuple()
        direction = _dir_from_angle(float(ship.rotation_deg))
        bullet_vel = Vec2(
            ship.kinematic.velocity.x + (direction.x * self.bullet_speed),
            ship.kinematic.velocity.y + (direction.y * self.bullet_speed),
        )
        return build_bullet(
            entity_id=bullet_id,
            pos=Vec2(sx, sy),
            vel=bullet_vel,
            template=world.entity_templates.get("bullet"),
            viewport=world.viewport,
        )

    def _after_spawn(
        self,
        ctx: AsteroidsTickContext,
        _spawned: tuple[BaseEntity, ...],
    ) -> None:
        ship = _ship(ctx.world)
        if ship is not None:
            ship.fire_cd = self.fire_cooldown

    def step(self, ctx: AsteroidsTickContext) -> None:
        """Tick bullet cooldowns and delegate bullet spawning."""

        ship = _ship(ctx.world)
        if ship is not None:
            ship.fire_cd = max(
                0.0, float(getattr(ship, "fire_cd", 0.0)) - ctx.dt
            )
        self._spawn.step(ctx)


@dataclass
class ShipStatusTimerSystem:
    """Ticks ship respawn and invulnerability timers."""

    name: str = "asteroids_ship_status_timers"
    phase: int = SystemPhase.SIMULATION
    order: int = 29

    def step(self, ctx: AsteroidsTickContext) -> None:
        """Tick ship respawn and invulnerability timers."""

        ship = _ship(ctx.world)
        if ship is None:
            return

        ship.respawn_timer = max(
            0.0, float(getattr(ship, "respawn_timer", 0.0)) - ctx.dt
        )
        ship.invuln_timer = max(
            0.0, float(getattr(ship, "invuln_timer", 0.0)) - ctx.dt
        )


@dataclass
class WorldMotionBundle(SystemBundle[AsteroidsTickContext]):
    """
    Bundle of processors that integrate world motion and viewport policies.
    """

    ship_drag: float = 0.992
    _motion: KinematicMotionSystem[AsteroidsTickContext] = field(
        init=False,
        repr=False,
    )
    _constraints: ViewportConstraintSystem[AsteroidsTickContext] = field(
        init=False,
        repr=False,
    )
    _ship_timers: ShipStatusTimerSystem = field(init=False, repr=False)
    _projectiles: ProjectileLifecycleBundle[AsteroidsTickContext] = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        def _ship_entities(ctx: AsteroidsTickContext):
            ship = _ship(ctx.world)
            if ship is None:
                return ()
            return (ship,)

        self._motion = KinematicMotionSystem(
            bindings=(
                MotionBinding(
                    entities_getter=_ship_entities,
                    predicate=lambda ctx, ship: (
                        (not ctx.world.game_over)
                        and float(getattr(ship, "respawn_timer", 0.0)) <= 0.0
                    ),
                    drag=self.ship_drag,
                ),
                MotionBinding(
                    entities_getter=lambda ctx: _asteroids(ctx.world),
                    spin_attr="spin_deg",
                ),
                MotionBinding(
                    entities_getter=lambda ctx: _bullets(ctx.world),
                    ttl_step=True,
                ),
            ),
        )
        self._constraints = ViewportConstraintSystem(
            bindings=(
                ViewportConstraintBinding(
                    entities_getter=_ship_entities,
                    policy="wrap",
                ),
                ViewportConstraintBinding(
                    entities_getter=lambda ctx: _asteroids(ctx.world),
                    policy="wrap",
                ),
                ViewportConstraintBinding(
                    entities_getter=lambda ctx: _bullets(ctx.world),
                    policy="cull",
                    margin_getter=lambda _ctx, bullet: float(
                        getattr(bullet, "radius", 2.5)
                    ),
                    on_cull=lambda _ctx, bullet: (
                        setattr(bullet.life, "alive", False)
                        if bullet.life is not None
                        else None
                    ),
                ),
            ),
        )
        self._ship_timers = ShipStatusTimerSystem()
        self._projectiles = ProjectileLifecycleBundle(
            bindings=(
                ProjectileLifecycleBinding(
                    entities_getter=lambda ctx: _bullets(ctx.world),
                    predicate=lambda _ctx, bullet: (
                        bullet.life is None or bullet.life.alive
                    ),
                    ttl_step=True,
                    margin_getter=lambda _ctx, bullet: float(
                        getattr(bullet, "radius", 2.5)
                    ),
                ),
            ),
            motion_name="asteroids_projectile_motion",
            motion_order=31,
            boundary_name="asteroids_projectile_boundary",
            boundary_order=41,
            cleanup_name="asteroids_projectile_cleanup",
            cleanup_order=42,
        )

    def iter_systems(self) -> Iterable[object]:
        return (
            self._ship_timers,
            self._motion,
            self._constraints,
            self._projectiles,
        )


MotionSystem = WorldMotionBundle


@dataclass
class CollisionSystem:
    """
    Resolve bullet/asteroid and ship/asteroid collisions.
    """

    name: str = "asteroids_collision"
    phase: int = SystemPhase.SIMULATION
    order: int = 40
    respawn_lock_s: float = 1.1
    invuln_s: float = 2.0

    @staticmethod
    def _split_asteroid(
        world: AsteroidsWorld,
        parent: BaseEntity,
        reserved_ids: set[int] | None = None,
    ) -> list[BaseEntity]:
        parent_size = int(getattr(parent, "size_level", 1))
        if parent_size <= 1:
            return []

        wave_spec = resolve_wave_spawn_spec(world)
        split_spec = wave_spec.split
        asteroid_template = world.entity_templates.get("asteroid")
        child_size = parent_size - 1
        child_radius = max(
            float(split_spec.min_radius),
            float(getattr(parent, "radius", 20.0))
            * float(split_spec.radius_scale),
        )
        out: list[BaseEntity] = []
        pvx = parent.kinematic.velocity.x if parent.kinematic else 0.0
        pvy = parent.kinematic.velocity.y if parent.kinematic else 0.0
        base_speed = max(
            float(split_spec.base_speed_min),
            math.hypot(pvx, pvy),
        )

        for _ in range(2):
            asteroid_id = world.allocate_entity_id_for(
                "asteroid",
                reserved_ids=reserved_ids,
            )
            if asteroid_id is None:
                continue
            if reserved_ids is not None:
                reserved_ids.add(asteroid_id)
            heading = random.uniform(0.0, math.tau)
            speed = base_speed * random.uniform(
                float(split_spec.speed_scale_min),
                float(split_spec.speed_scale_max),
            )
            out.append(
                build_asteroid(
                    entity_id=asteroid_id,
                    pos=Vec2(
                        parent.transform.center.x, parent.transform.center.y
                    ),
                    vel=Vec2(
                        pvx * 0.25 + math.cos(heading) * speed,
                        pvy * 0.25 + math.sin(heading) * speed,
                    ),
                    radius=child_radius,
                    size_level=child_size,
                    angle_deg=random.uniform(0.0, 360.0),
                    spin_deg=random.uniform(
                        float(split_spec.spin_range[0]),
                        float(split_spec.spin_range[-1]),
                    ),
                    points=make_asteroid_points(wave_spec),
                    template=asteroid_template,
                    viewport=world.viewport,
                )
            )
        return out

    def _resolve_bullet_hits(self, ctx: AsteroidsTickContext):
        world = ctx.world
        bullets = _bullets(world)
        asteroids = _asteroids(world)
        if not bullets or not asteroids:
            return

        removed_bullets: set[int] = set()
        removed_asteroids: set[int] = set()
        spawned: list[BaseEntity] = []
        reserved_spawn_ids: set[int] = set()
        score_by_size = {3: 20, 2: 50, 1: 100}

        for bullet in bullets:
            if int(bullet.id) in removed_bullets:
                continue
            bp = bullet.transform.center
            br = float(getattr(bullet, "radius", 2.5))
            for asteroid in asteroids:
                aid = int(asteroid.id)
                if aid in removed_asteroids:
                    continue
                hit_r = br + float(getattr(asteroid, "radius", 0.0))
                if _distance2(bp, asteroid.transform.center) > (hit_r * hit_r):
                    continue
                removed_bullets.add(int(bullet.id))
                removed_asteroids.add(aid)
                world.score += score_by_size.get(
                    int(getattr(asteroid, "size_level", 1)), 0
                )
                spawned.extend(
                    self._split_asteroid(
                        world, asteroid, reserved_ids=reserved_spawn_ids
                    )
                )
                break

        if removed_bullets or removed_asteroids:
            world.remove_entities_by_ids(removed_bullets | removed_asteroids)
        if spawned:
            world.entities.extend(spawned)

    def _resolve_ship_hit(self, ctx: AsteroidsTickContext):
        world = ctx.world
        ship = _ship(world)
        if ship is None or ship.kinematic is None:
            return
        if world.game_over:
            return
        if float(getattr(ship, "respawn_timer", 0.0)) > 0.0:
            return
        if float(getattr(ship, "invuln_timer", 0.0)) > 0.0:
            return

        ship_radius = float(getattr(ship, "ship_radius", 12.0))
        for asteroid in _asteroids(world):
            hit_r = (
                ship_radius + float(getattr(asteroid, "radius", 0.0)) * 0.82
            )
            if _distance2(ship.transform.center, asteroid.transform.center) > (
                hit_r * hit_r
            ):
                continue

            world.lives = max(0, world.lives - 1)
            ship.kinematic.velocity = Vec2(0.0, 0.0)
            ship.ship_thrusting = False
            ship.rotation_deg = -90.0

            spawn_x, spawn_y = world.ship_spawn_position
            ship.transform.center = Vec2(spawn_x, spawn_y)

            bullet_ids = {int(b.id) for b in _bullets(world)}
            if bullet_ids:
                world.remove_entities_by_ids(bullet_ids)

            if world.lives <= 0:
                world.game_over = True
                ship.respawn_timer = 0.0
                ship.invuln_timer = 0.0
            else:
                ship.respawn_timer = self.respawn_lock_s
                ship.invuln_timer = self.invuln_s
            return

    def step(self, ctx: AsteroidsTickContext):
        """Resolve bullet and ship collisions against the asteroid field."""

        self._resolve_bullet_hits(ctx)
        self._resolve_ship_hit(ctx)


@dataclass
class AsteroidsWaveProgressionSystem:
    """
    Advance asteroid waves when the playfield has been cleared.
    """

    name: str = "asteroids_wave_progression"
    phase: int = SystemPhase.SIMULATION
    order: int = 50
    _waves: WaveProgressionSystem[AsteroidsTickContext] = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        def _can_progress(ctx: AsteroidsTickContext) -> bool:
            ship = _ship(ctx.world)
            return bool(
                ship is not None
                and ship.kinematic is not None
                and not ctx.world.game_over
            )

        def _advance(ctx: AsteroidsTickContext) -> None:
            world = ctx.world
            ship = _ship(world)
            if ship is None or ship.kinematic is None:
                return

            world.level += 1
            spawn_x, spawn_y = world.ship_spawn_position
            ship.transform.center = Vec2(spawn_x, spawn_y)
            ship.kinematic.velocity = Vec2(0.0, 0.0)
            ship.rotation_deg = -90.0
            ship.respawn_timer = max(
                float(getattr(ship, "respawn_timer", 0.0)),
                0.7,
            )
            ship.invuln_timer = max(
                float(getattr(ship, "invuln_timer", 0.0)),
                1.6,
            )

        def _spawn_next(ctx: AsteroidsTickContext) -> list[BaseEntity]:
            world = ctx.world
            ship = _ship(world)
            if ship is None:
                return []

            wave_spec = resolve_wave_spawn_spec(world)
            count = min(
                int(wave_spec.max_count),
                int(wave_spec.base_count)
                + (world.level * int(wave_spec.count_per_level)),
            )
            return spawn_asteroid_wave(
                world=world,
                ship_pos=ship.transform.center,
                level=world.level,
                count=count,
                spec=wave_spec,
            )

        self._waves = WaveProgressionSystem(
            name=self.name,
            phase=self.phase,
            order=self.order,
            bindings=(
                WaveProgressionBinding(
                    is_complete=lambda ctx: not _asteroids(ctx.world),
                    can_progress=_can_progress,
                    advance=_advance,
                    spawn_next=_spawn_next,
                ),
            ),
        )

    def step(self, ctx: AsteroidsTickContext) -> None:
        """Advance the wave helper once the current field has been cleared."""

        self._waves.step(ctx)
