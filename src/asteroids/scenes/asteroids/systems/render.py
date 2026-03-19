"""Rendering system for Asteroids scene."""

from __future__ import annotations

import math
from dataclasses import dataclass

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.systems.builtins import (
    ConfiguredQueuedRenderSystem,
    RenderOverlay,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase
from mini_arcade_core.spaces.math.vec2 import Vec2

from asteroids.scenes.asteroids.draw_ops import DrawHud
from asteroids.scenes.asteroids.models import AsteroidsTickContext


def _rotate_point(x: float, y: float, angle_deg: float) -> tuple[float, float]:
    rad = math.radians(angle_deg)
    cs = math.cos(rad)
    sn = math.sin(rad)
    return (x * cs - y * sn, x * sn + y * cs)


@dataclass
class AsteroidsRenderSystem(
    ConfiguredQueuedRenderSystem[AsteroidsTickContext]
):
    """
    Built-in vector rendering for world entities, plus HUD and ship thrust.
    """

    name: str = "asteroids_render"
    phase: int = SystemPhase.RENDERING
    order: int = 100
    overlays: tuple[RenderOverlay[AsteroidsTickContext], ...] = (
        RenderOverlay.from_drawable(DrawHud(), layer="ui", z=100),
    )

    def emit_entity(
        self, ctx: AsteroidsTickContext, rq: object, entity: BaseEntity
    ) -> None:
        ship = ctx.world.ship()
        if ship is None or entity is not ship:
            super().emit_entity(ctx, rq, entity)
            return

        if (
            ctx.world.game_over
            or float(getattr(ship, "respawn_timer", 0.0)) > 0.0
        ):
            return

        self.emit_default_entity(ctx, rq, entity)

        if not bool(getattr(ship, "ship_thrusting", False)):
            return

        sx, sy = ship.transform.center.to_tuple()
        ship_angle = float(getattr(ship, "rotation_deg", -90.0))
        thrust_color = getattr(ship, "thrust_color", (255, 150, 90, 255))

        tail = _rotate_point(0.0, 11.0, ship_angle)
        flame_a = _rotate_point(-4.0, 10.0, ship_angle)
        flame_b = _rotate_point(+4.0, 10.0, ship_angle)
        flame_c = _rotate_point(0.0, 18.0, ship_angle)

        tail_vec = Vec2(sx + tail[0], sy + tail[1])
        flame_a_vec = Vec2(sx + flame_a[0], sy + flame_a[1])
        flame_b_vec = Vec2(sx + flame_b[0], sy + flame_b[1])
        flame_c_vec = Vec2(sx + flame_c[0], sy + flame_c[1])

        rq.line(
            a=tail_vec,
            b=flame_c_vec,
            color=thrust_color,
            thickness=1.0,
            layer="world",
            z=ship.z_index,
        )
        rq.line(
            a=flame_a_vec,
            b=flame_c_vec,
            color=thrust_color,
            thickness=1.0,
            layer="world",
            z=ship.z_index,
        )
        rq.line(
            a=flame_b_vec,
            b=flame_c_vec,
            color=thrust_color,
            thickness=1.0,
            layer="world",
            z=ship.z_index,
        )
