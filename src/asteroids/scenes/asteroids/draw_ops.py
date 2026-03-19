"""
Draw operations for Asteroids gameplay.
"""

from __future__ import annotations

import math

from mini_arcade_core.backend import Backend
from mini_arcade_core.scenes.sim_scene import Drawable

from asteroids.scenes.asteroids.models import AsteroidsTickContext


def _rotate_point(x: float, y: float, angle_deg: float) -> tuple[float, float]:
    rad = math.radians(angle_deg)
    cs = math.cos(rad)
    sn = math.sin(rad)
    return (x * cs - y * sn, x * sn + y * cs)


class DrawWorld(Drawable[AsteroidsTickContext]):
    """
    Draw ship, bullets, and asteroids.
    """

    ship_color = (240, 240, 245, 255)
    thrust_color = (255, 150, 90, 255)
    asteroid_color = (200, 210, 230, 255)
    bullet_color = (255, 255, 255, 255)

    def draw(self, backend: Backend, ctx: AsteroidsTickContext):
        world = ctx.world

        for asteroid in world.asteroids():
            if asteroid.kinematic is None:
                continue
            points = getattr(asteroid, "points", ())
            radius = float(getattr(asteroid, "radius", 0.0))
            angle = float(getattr(asteroid, "rotation_deg", 0.0))
            cx, cy = asteroid.transform.center.to_tuple()

            poly: list[tuple[int, int]] = []
            for px, py in points:
                rx, ry = _rotate_point(float(px), float(py), angle)
                poly.append((int(cx + rx * radius), int(cy + ry * radius)))
            if len(poly) >= 3:
                backend.render.draw_poly(
                    poly, color=self.asteroid_color, filled=False
                )

        for bullet in world.bullets():
            bx, by = bullet.transform.center.to_tuple()
            r = float(getattr(bullet, "radius", 2.5))
            backend.render.draw_rect(
                int(bx - r),
                int(by - r),
                int(r * 2.0),
                int(r * 2.0),
                color=self.bullet_color,
            )

        ship = world.ship()
        if ship is None:
            return
        if world.game_over or float(getattr(ship, "respawn_timer", 0.0)) > 0.0:
            return

        sx, sy = ship.transform.center.to_tuple()
        ship_angle = float(getattr(ship, "rotation_deg", -90.0))
        ship_pts_local = ((0.0, -14.0), (10.0, 10.0), (-10.0, 10.0))
        ship_pts: list[tuple[int, int]] = []
        for px, py in ship_pts_local:
            rx, ry = _rotate_point(px, py, ship_angle)
            ship_pts.append((int(sx + rx), int(sy + ry)))
        backend.render.draw_poly(ship_pts, color=self.ship_color, filled=False)

        if not bool(getattr(ship, "ship_thrusting", False)):
            return

        tail = _rotate_point(0.0, 11.0, ship_angle)
        flame_a = _rotate_point(-4.0, 10.0, ship_angle)
        flame_b = _rotate_point(+4.0, 10.0, ship_angle)
        flame_c = _rotate_point(0.0, 18.0, ship_angle)
        ax = int(sx + flame_a[0])
        ay = int(sy + flame_a[1])
        bx = int(sx + flame_b[0])
        by = int(sy + flame_b[1])
        cx = int(sx + flame_c[0])
        cy = int(sy + flame_c[1])
        tx = int(sx + tail[0])
        ty = int(sy + tail[1])
        backend.render.draw_line(tx, ty, cx, cy, color=self.thrust_color)
        backend.render.draw_line(ax, ay, cx, cy, color=self.thrust_color)
        backend.render.draw_line(bx, by, cx, cy, color=self.thrust_color)


class DrawHud(Drawable[AsteroidsTickContext]):
    """
    Draw game HUD and overlays.
    """

    hud_color = (220, 230, 245, 255)
    warn_color = (255, 130, 120, 255)

    def draw(self, backend: Backend, ctx: AsteroidsTickContext):
        world = ctx.world
        vw, vh = backend.window.size()
        vw = int(vw)
        vh = int(vh)

        backend.text.draw(
            12,
            12,
            f"SCORE {int(world.score):06d}",
            color=self.hud_color,
        )
        backend.text.draw(
            vw - 160,
            12,
            f"LIVES {int(world.lives)}",
            color=self.hud_color,
        )
        backend.text.draw(
            vw // 2 - 50,
            12,
            f"LEVEL {int(world.level)}",
            color=self.hud_color,
        )

        ship = world.ship()
        ship_respawn = (
            float(getattr(ship, "respawn_timer", 0.0)) if ship else 0.0
        )
        if ship_respawn > 0.0 and not world.game_over:
            msg = "READY..."
            tw, _ = backend.text.measure(msg)
            backend.text.draw(
                (vw - tw) // 2,
                vh - 40,
                msg,
                color=(180, 220, 255, 255),
            )

        if not world.game_over:
            return

        title = "GAME OVER"
        hint = "ENTER RESTART FROM PAUSE MENU"
        tw, _ = backend.text.measure(title)
        hw, _ = backend.text.measure(hint)
        backend.text.draw(
            (vw - tw) // 2,
            (vh // 2) - 20,
            title,
            color=self.warn_color,
        )
        backend.text.draw(
            (vw - hw) // 2,
            (vh // 2) + 18,
            hint,
            color=self.hud_color,
        )
