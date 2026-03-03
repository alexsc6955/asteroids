"""
Systems for Asteroids gameplay.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.runtime.services import RuntimeServices
from mini_arcade_core.scenes.sim_scene import DrawCall
from mini_arcade_core.scenes.systems.builtins import (
    ActionIntentSystem,
    ActionMap,
    AxisActionBinding,
    BaseQueuedRenderSystem,
    CaptureHotkeysConfig,
    CaptureHotkeysSystem,
    DigitalActionBinding,
)
from mini_arcade_core.spaces.math.vec2 import Vec2

from asteroids.entities import EntityId, build_asteroid, build_bullet
from asteroids.scenes.asteroids.draw_ops import DrawHud, DrawWorld
from asteroids.scenes.asteroids.models import (
    AsteroidsIntent,
    AsteroidsTickContext,
    AsteroidsWorld,
)
from asteroids.scenes.commands import PauseAsteroidsCommand


ASTEROIDS_ACTIONS = ActionMap(
    bindings={
        "rotate": AxisActionBinding(
            positive_keys=(Key.RIGHT, Key.D),
            negative_keys=(Key.LEFT, Key.A),
        ),
        "thrust": DigitalActionBinding(keys=(Key.UP, Key.W)),
        "fire": DigitalActionBinding(keys=(Key.SPACE,)),
        "pause": DigitalActionBinding(keys=(Key.ESCAPE,)),
        "capture_toggle_replay_record": DigitalActionBinding(keys=(Key.F10,)),
        "capture_toggle_replay_play": DigitalActionBinding(keys=(Key.F11,)),
        "capture_toggle_video": DigitalActionBinding(keys=(Key.F12,)),
    }
)

ASTEROIDS_MENU_CAPTURE_ACTIONS = ActionMap(
    bindings={
        "capture_toggle_video": DigitalActionBinding(keys=(Key.F12,)),
    }
)


def _build_asteroids_intent(
    actions,
    _ctx: AsteroidsTickContext,
) -> AsteroidsIntent:
    rotate_axis = actions.value("rotate")
    return AsteroidsIntent(
        rotate_left=rotate_axis < -0.1,
        rotate_right=rotate_axis > 0.1,
        thrust=actions.down("thrust"),
        fire=actions.pressed("fire"),
        pause=actions.pressed("pause"),
    )


def build_asteroids_game_capture_hotkeys_system(
    services: RuntimeServices,
) -> CaptureHotkeysSystem:
    return CaptureHotkeysSystem(
        services=services,
        action_map=ASTEROIDS_ACTIONS,
        cfg=CaptureHotkeysConfig(
            replay_file="asteroids_replay.marc",
            replay_game_id="asteroids",
            replay_initial_scene="asteroids",
            action_toggle_video="capture_toggle_video",
            action_toggle_replay_record="capture_toggle_replay_record",
            action_toggle_replay_play="capture_toggle_replay_play",
        ),
    )


def build_asteroids_menu_capture_hotkeys_system(
    services: RuntimeServices,
) -> CaptureHotkeysSystem:
    return CaptureHotkeysSystem(
        services=services,
        action_map=ASTEROIDS_MENU_CAPTURE_ACTIONS,
        cfg=CaptureHotkeysConfig(
            replay_file=None,
            action_toggle_video="capture_toggle_video",
        ),
    )


def _distance2(a: Vec2, b: Vec2) -> float:
    dx = a.x - b.x
    dy = a.y - b.y
    return dx * dx + dy * dy


def _wrap(value: float, limit: float) -> float:
    if limit <= 0:
        return value
    if value < 0.0:
        return value + limit
    if value >= limit:
        return value - limit
    return value


def _dir_from_angle(angle_deg: float) -> Vec2:
    # Ship mesh points "up" when angle is 0, so gameplay forward is angle-90.
    rad = math.radians(angle_deg - 90.0)
    return Vec2(math.cos(rad), math.sin(rad))


def _make_asteroid_points() -> tuple[tuple[float, float], ...]:
    count = random.randint(8, 12)
    out: list[tuple[float, float]] = []
    for i in range(count):
        angle = (math.tau * float(i)) / float(count)
        r = random.uniform(0.72, 1.15)
        out.append((math.cos(angle) * r, math.sin(angle) * r))
    return tuple(out)


def _alloc_entity_id(
    world: AsteroidsWorld,
    start: int,
    end: int,
    reserved_ids: set[int] | None = None,
) -> int | None:
    used = {int(e.id) for e in world.entities if start <= int(e.id) <= end}
    if reserved_ids:
        used |= {rid for rid in reserved_ids if start <= rid <= end}
    for candidate in range(int(start), int(end) + 1):
        if candidate not in used:
            return candidate
    return None


def _ship(world: AsteroidsWorld) -> BaseEntity | None:
    return world.ship()


def _asteroids(world: AsteroidsWorld) -> list[BaseEntity]:
    return world.asteroids()


def _bullets(world: AsteroidsWorld) -> list[BaseEntity]:
    return world.bullets()


def _remove_ids(world: AsteroidsWorld, ids: set[int]) -> None:
    world.entities = [e for e in world.entities if int(e.id) not in ids]


def spawn_asteroid_wave(
    *,
    world: AsteroidsWorld,
    ship_pos: Vec2,
    level: int,
    count: int,
) -> list[BaseEntity]:
    """
    Spawn a wave of large asteroids away from the ship.
    """
    vw, vh = world.viewport
    out: list[BaseEntity] = []
    min_dist = min(vw, vh) * 0.26
    reserved_spawn_ids: set[int] = set()

    for _ in range(count):
        px = random.uniform(0.0, vw)
        py = random.uniform(0.0, vh)
        for _attempt in range(40):
            if _distance2(Vec2(px, py), ship_pos) >= (min_dist * min_dist):
                break
            px = random.uniform(0.0, vw)
            py = random.uniform(0.0, vh)

        speed = random.uniform(28.0 + level * 1.5, 64.0 + level * 3.0)
        heading = random.uniform(0.0, math.tau)
        vx = math.cos(heading) * speed
        vy = math.sin(heading) * speed
        asteroid_id = _alloc_entity_id(
            world,
            int(EntityId.ASTEROID_START),
            int(EntityId.ASTEROID_END),
            reserved_ids=reserved_spawn_ids,
        )
        if asteroid_id is None:
            continue
        reserved_spawn_ids.add(asteroid_id)
        out.append(
            build_asteroid(
                entity_id=asteroid_id,
                pos=Vec2(px, py),
                vel=Vec2(vx, vy),
                radius=random.uniform(34.0, 52.0),
                size_level=3,
                angle_deg=random.uniform(0.0, 360.0),
                spin_deg=random.uniform(-28.0, 28.0),
                points=_make_asteroid_points(),
            )
        )
    return out


class AsteroidsInputSystem(
    ActionIntentSystem[AsteroidsTickContext, AsteroidsIntent]
):
    """
    Build gameplay intent from action-map bindings.
    """

    def __init__(self):
        super().__init__(
            action_map=ASTEROIDS_ACTIONS,
            intent_factory=_build_asteroids_intent,
            name="asteroids_input",
        )


@dataclass
class AsteroidsPauseSystem:
    """
    Push pause scene when requested.
    """

    name: str = "asteroids_pause"
    order: int = 12

    def step(self, ctx: AsteroidsTickContext):
        if ctx.intent is None or not ctx.intent.pause:
            return
        ctx.commands.push(PauseAsteroidsCommand())


@dataclass
class ShipControlSystem:
    """
    Rotate/thrust ship and spawn bullets.
    """

    name: str = "asteroids_ship_control"
    order: int = 20

    turn_speed_deg: float = 240.0
    thrust_accel: float = 280.0
    max_speed: float = 330.0
    fire_cooldown: float = 0.18
    bullet_speed: float = 460.0

    def step(self, ctx: AsteroidsTickContext):
        world = ctx.world
        ship = _ship(world)
        intent = ctx.intent
        if ship is None or ship.kinematic is None:
            return
        if intent is None or world.game_over:
            ship.ship_thrusting = False
            return

        ship.fire_cd = max(0.0, float(getattr(ship, "fire_cd", 0.0)) - ctx.dt)
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

        speed = math.hypot(ship.kinematic.velocity.x, ship.kinematic.velocity.y)
        if speed > self.max_speed and speed > 0.0:
            scale = self.max_speed / speed
            ship.kinematic.velocity.x *= scale
            ship.kinematic.velocity.y *= scale

        if not intent.fire or float(getattr(ship, "fire_cd", 0.0)) > 0.0:
            return

        bullet_id = _alloc_entity_id(
            world,
            int(EntityId.BULLET_START),
            int(EntityId.BULLET_END),
        )
        if bullet_id is None:
            return
        sx, sy = ship.transform.center.to_tuple()
        d = _dir_from_angle(float(ship.rotation_deg))
        bullet_vel = Vec2(
            ship.kinematic.velocity.x + (d.x * self.bullet_speed),
            ship.kinematic.velocity.y + (d.y * self.bullet_speed),
        )
        world.entities.append(
            build_bullet(
                entity_id=bullet_id,
                pos=Vec2(sx, sy),
                vel=bullet_vel,
            )
        )
        ship.fire_cd = self.fire_cooldown


@dataclass
class MotionSystem:
    """
    Integrate motion, wrap ship/asteroids, and cull off-screen bullets.
    """

    name: str = "asteroids_motion"
    order: int = 30
    ship_drag: float = 0.992

    def step(self, ctx: AsteroidsTickContext):
        world = ctx.world
        ship = _ship(world)
        vw, vh = world.viewport

        if ship is not None:
            ship.respawn_timer = max(
                0.0, float(getattr(ship, "respawn_timer", 0.0)) - ctx.dt
            )
            ship.invuln_timer = max(
                0.0, float(getattr(ship, "invuln_timer", 0.0)) - ctx.dt
            )

        if (
            ship is not None
            and ship.kinematic is not None
            and not world.game_over
            and float(getattr(ship, "respawn_timer", 0.0)) <= 0.0
        ):
            ship.transform.center.x += ship.kinematic.velocity.x * ctx.dt
            ship.transform.center.y += ship.kinematic.velocity.y * ctx.dt
            ship.transform.center.x = _wrap(ship.transform.center.x, vw)
            ship.transform.center.y = _wrap(ship.transform.center.y, vh)
            ship.kinematic.velocity.x *= self.ship_drag
            ship.kinematic.velocity.y *= self.ship_drag

        for asteroid in _asteroids(world):
            if asteroid.kinematic is None:
                continue
            asteroid.transform.center.x = _wrap(
                asteroid.transform.center.x + asteroid.kinematic.velocity.x * ctx.dt,
                vw,
            )
            asteroid.transform.center.y = _wrap(
                asteroid.transform.center.y + asteroid.kinematic.velocity.y * ctx.dt,
                vh,
            )
            asteroid.rotation_deg = (
                float(getattr(asteroid, "rotation_deg", 0.0))
                + float(getattr(asteroid, "spin_deg", 0.0)) * ctx.dt
            ) % 360.0

        dead_ids: set[int] = set()
        for bullet in _bullets(world):
            if bullet.kinematic is None or bullet.life is None:
                dead_ids.add(int(bullet.id))
                continue
            bullet.transform.center.x += bullet.kinematic.velocity.x * ctx.dt
            bullet.transform.center.y += bullet.kinematic.velocity.y * ctx.dt
            radius = float(getattr(bullet, "radius", 2.5))
            if (
                bullet.transform.center.x < -radius
                or bullet.transform.center.x > (vw + radius)
                or bullet.transform.center.y < -radius
                or bullet.transform.center.y > (vh + radius)
            ):
                bullet.life.alive = False
            if bullet.life.ttl is not None:
                bullet.life.ttl -= ctx.dt
                if bullet.life.ttl <= 0.0:
                    bullet.life.alive = False
            if not bullet.life.alive:
                dead_ids.add(int(bullet.id))
        if dead_ids:
            _remove_ids(world, dead_ids)


@dataclass
class CollisionSystem:
    """
    Resolve bullet/asteroid and ship/asteroid collisions.
    """

    name: str = "asteroids_collision"
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

        child_size = parent_size - 1
        child_radius = max(10.0, float(getattr(parent, "radius", 20.0)) * 0.62)
        out: list[BaseEntity] = []
        pvx = parent.kinematic.velocity.x if parent.kinematic else 0.0
        pvy = parent.kinematic.velocity.y if parent.kinematic else 0.0
        base_speed = max(80.0, math.hypot(pvx, pvy))

        for _ in range(2):
            asteroid_id = _alloc_entity_id(
                world,
                int(EntityId.ASTEROID_START),
                int(EntityId.ASTEROID_END),
                reserved_ids=reserved_ids,
            )
            if asteroid_id is None:
                continue
            if reserved_ids is not None:
                reserved_ids.add(asteroid_id)
            heading = random.uniform(0.0, math.tau)
            speed = base_speed * random.uniform(0.75, 1.18)
            out.append(
                build_asteroid(
                    entity_id=asteroid_id,
                    pos=Vec2(parent.transform.center.x, parent.transform.center.y),
                    vel=Vec2(
                        pvx * 0.25 + math.cos(heading) * speed,
                        pvy * 0.25 + math.sin(heading) * speed,
                    ),
                    radius=child_radius,
                    size_level=child_size,
                    angle_deg=random.uniform(0.0, 360.0),
                    spin_deg=random.uniform(-48.0, 48.0),
                    points=_make_asteroid_points(),
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
                if (
                    _distance2(bp, asteroid.transform.center)
                    > (hit_r * hit_r)
                ):
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
            _remove_ids(world, removed_bullets | removed_asteroids)
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
            hit_r = ship_radius + float(getattr(asteroid, "radius", 0.0)) * 0.82
            if (
                _distance2(ship.transform.center, asteroid.transform.center)
                > (hit_r * hit_r)
            ):
                continue

            world.lives = max(0, world.lives - 1)
            ship.kinematic.velocity = Vec2(0.0, 0.0)
            ship.ship_thrusting = False
            ship.rotation_deg = -90.0

            vw, vh = world.viewport
            ship.transform.center = Vec2(vw * 0.5, vh * 0.5)

            bullet_ids = {int(b.id) for b in _bullets(world)}
            if bullet_ids:
                _remove_ids(world, bullet_ids)

            if world.lives <= 0:
                world.game_over = True
                ship.respawn_timer = 0.0
                ship.invuln_timer = 0.0
            else:
                ship.respawn_timer = self.respawn_lock_s
                ship.invuln_timer = self.invuln_s
            return

    def _advance_level_if_cleared(self, ctx: AsteroidsTickContext):
        world = ctx.world
        ship = _ship(world)
        if ship is None or ship.kinematic is None:
            return
        if world.game_over or _asteroids(world):
            return

        world.level += 1
        vw, vh = world.viewport
        ship.transform.center = Vec2(vw * 0.5, vh * 0.5)
        ship.kinematic.velocity = Vec2(0.0, 0.0)
        ship.rotation_deg = -90.0
        ship.respawn_timer = max(float(getattr(ship, "respawn_timer", 0.0)), 0.7)
        ship.invuln_timer = max(float(getattr(ship, "invuln_timer", 0.0)), 1.6)

        count = min(14, 3 + world.level)
        world.entities.extend(
            spawn_asteroid_wave(
                world=world,
                ship_pos=ship.transform.center,
                level=world.level,
                count=count,
            )
        )

    def step(self, ctx: AsteroidsTickContext):
        self._resolve_bullet_hits(ctx)
        self._resolve_ship_hit(ctx)
        self._advance_level_if_cleared(ctx)


@dataclass
class AsteroidsRenderSystem(
    BaseQueuedRenderSystem[AsteroidsTickContext]
):
    """
    Queue world and HUD drawables into render passes.
    """

    name: str = "asteroids_render"
    order: int = 100

    def emit(self, ctx: AsteroidsTickContext, rq):
        rq.custom(
            op=DrawCall(drawable=DrawWorld(), ctx=ctx),
            layer="world",
            z=10,
        )
        rq.custom(
            op=DrawCall(drawable=DrawHud(), ctx=ctx),
            layer="ui",
            z=100,
        )
