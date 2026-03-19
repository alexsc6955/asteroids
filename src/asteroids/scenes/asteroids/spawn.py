"""
Spawn policies for Asteroids gameplay.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.spaces.math.vec2 import Vec2

from asteroids.entities import build_asteroid
from asteroids.scenes.asteroids.models import AsteroidsWorld


@dataclass(frozen=True)
class AsteroidSplitSpec:
    """Tuning values used when a large asteroid splits into smaller ones."""

    min_radius: float = 10.0
    radius_scale: float = 0.62
    base_speed_min: float = 80.0
    speed_scale_min: float = 0.75
    speed_scale_max: float = 1.18
    spin_range: tuple[float, float] = (-48.0, 48.0)


@dataclass(frozen=True)
class AsteroidWaveSpawnSpec:
    """Tuning values used when generating a fresh asteroid wave."""

    initial_count: int = 5
    base_count: int = 3
    count_per_level: int = 1
    max_count: int = 14
    min_spawn_distance_ratio: float = 0.26
    speed_min_base: float = 28.0
    speed_min_per_level: float = 1.5
    speed_max_base: float = 64.0
    speed_max_per_level: float = 3.0
    radius_range: tuple[float, float] = (34.0, 52.0)
    size_level: int = 3
    spin_range: tuple[float, float] = (-28.0, 28.0)
    point_count_range: tuple[int, int] = (8, 12)
    point_radius_range: tuple[float, float] = (0.72, 1.15)
    split: AsteroidSplitSpec = AsteroidSplitSpec()


def asteroid_wave_spawn_spec(
    raw_cfg: dict[str, object] | None = None,
) -> AsteroidWaveSpawnSpec:
    """
    Normalize raw wave config into a typed spawn spec.
    """
    raw_cfg = raw_cfg or {}
    split_cfg = raw_cfg.get("split", {}) or {}
    radius_range = raw_cfg.get("radius_range", [34.0, 52.0]) or [34.0, 52.0]
    spin_range = raw_cfg.get("spin_range", [-28.0, 28.0]) or [-28.0, 28.0]
    point_count_range = raw_cfg.get("point_count_range", [8, 12]) or [8, 12]
    point_radius_range = raw_cfg.get("point_radius_range", [0.72, 1.15]) or [
        0.72,
        1.15,
    ]
    split_spin_range = split_cfg.get("spin_range", [-48.0, 48.0]) or [
        -48.0,
        48.0,
    ]
    return AsteroidWaveSpawnSpec(
        initial_count=int(raw_cfg.get("initial_count", 5)),
        base_count=int(raw_cfg.get("base_count", 3)),
        count_per_level=int(raw_cfg.get("count_per_level", 1)),
        max_count=int(raw_cfg.get("max_count", 14)),
        min_spawn_distance_ratio=float(
            raw_cfg.get("min_spawn_distance_ratio", 0.26)
        ),
        speed_min_base=float(raw_cfg.get("speed_min_base", 28.0)),
        speed_min_per_level=float(raw_cfg.get("speed_min_per_level", 1.5)),
        speed_max_base=float(raw_cfg.get("speed_max_base", 64.0)),
        speed_max_per_level=float(raw_cfg.get("speed_max_per_level", 3.0)),
        radius_range=(float(radius_range[0]), float(radius_range[-1])),
        size_level=int(raw_cfg.get("size_level", 3)),
        spin_range=(float(spin_range[0]), float(spin_range[-1])),
        point_count_range=(
            int(point_count_range[0]),
            int(point_count_range[-1]),
        ),
        point_radius_range=(
            float(point_radius_range[0]),
            float(point_radius_range[-1]),
        ),
        split=AsteroidSplitSpec(
            min_radius=float(split_cfg.get("min_radius", 10.0)),
            radius_scale=float(split_cfg.get("radius_scale", 0.62)),
            base_speed_min=float(split_cfg.get("base_speed_min", 80.0)),
            speed_scale_min=float(split_cfg.get("speed_scale_min", 0.75)),
            speed_scale_max=float(split_cfg.get("speed_scale_max", 1.18)),
            spin_range=(
                float(split_spin_range[0]),
                float(split_spin_range[-1]),
            ),
        ),
    )


def resolve_wave_spawn_spec(
    world: AsteroidsWorld,
    spec: AsteroidWaveSpawnSpec | None = None,
) -> AsteroidWaveSpawnSpec:
    """
    Resolve the active wave spawn spec for a world.
    """
    return (
        spec
        or world.wave_spawn_spec
        or asteroid_wave_spawn_spec(world.wave_config)
    )


def _distance2(a: Vec2, b: Vec2) -> float:
    dx = a.x - b.x
    dy = a.y - b.y
    return dx * dx + dy * dy


def make_asteroid_points(
    spec: AsteroidWaveSpawnSpec,
) -> tuple[tuple[float, float], ...]:
    """Generate an irregular polygon outline for one asteroid."""

    count = random.randint(
        int(spec.point_count_range[0]),
        int(spec.point_count_range[-1]),
    )
    out: list[tuple[float, float]] = []
    for i in range(count):
        angle = (math.tau * float(i)) / float(count)
        radius = random.uniform(
            float(spec.point_radius_range[0]),
            float(spec.point_radius_range[-1]),
        )
        out.append((math.cos(angle) * radius, math.sin(angle) * radius))
    return tuple(out)


def spawn_asteroid_wave(
    *,
    world: AsteroidsWorld,
    ship_pos: Vec2,
    level: int,
    count: int,
    spec: AsteroidWaveSpawnSpec | None = None,
) -> list[BaseEntity]:
    """
    Spawn a wave of large asteroids away from the ship.
    """
    vw, vh = world.viewport
    wave_spec = resolve_wave_spawn_spec(world, spec)
    asteroid_template = world.entity_templates.get("asteroid")
    out: list[BaseEntity] = []
    min_dist = min(vw, vh) * float(wave_spec.min_spawn_distance_ratio)
    reserved_spawn_ids: set[int] = set()

    for _ in range(count):
        px = random.uniform(0.0, vw)
        py = random.uniform(0.0, vh)
        for _attempt in range(40):
            if _distance2(Vec2(px, py), ship_pos) >= (min_dist * min_dist):
                break
            px = random.uniform(0.0, vw)
            py = random.uniform(0.0, vh)

        speed = random.uniform(
            float(wave_spec.speed_min_base)
            + level * float(wave_spec.speed_min_per_level),
            float(wave_spec.speed_max_base)
            + level * float(wave_spec.speed_max_per_level),
        )
        heading = random.uniform(0.0, math.tau)
        vx = math.cos(heading) * speed
        vy = math.sin(heading) * speed
        asteroid_id = world.allocate_entity_id_for(
            "asteroid",
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
                radius=random.uniform(
                    float(wave_spec.radius_range[0]),
                    float(wave_spec.radius_range[-1]),
                ),
                size_level=int(wave_spec.size_level),
                angle_deg=random.uniform(0.0, 360.0),
                spin_deg=random.uniform(
                    float(wave_spec.spin_range[0]),
                    float(wave_spec.spin_range[-1]),
                ),
                points=make_asteroid_points(wave_spec),
                template=asteroid_template,
                viewport=world.viewport,
            )
        )
    return out


def spawn_initial_asteroid_wave(
    world: AsteroidsWorld,
    spec: AsteroidWaveSpawnSpec | None = None,
) -> list[BaseEntity]:
    """
    Spawn the opening asteroid batch for a newly created world.
    """
    wave_spec = resolve_wave_spawn_spec(world, spec)
    spawn_x, spawn_y = world.ship_spawn_position
    return spawn_asteroid_wave(
        world=world,
        ship_pos=Vec2(spawn_x, spawn_y),
        level=world.level,
        count=int(wave_spec.initial_count),
        spec=wave_spec,
    )


__all__ = [
    "AsteroidSplitSpec",
    "AsteroidWaveSpawnSpec",
    "asteroid_wave_spawn_spec",
    "make_asteroid_points",
    "resolve_wave_spawn_spec",
    "spawn_asteroid_wave",
    "spawn_initial_asteroid_wave",
]
