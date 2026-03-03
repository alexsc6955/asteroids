"""
Playable Asteroids scene.
"""

from __future__ import annotations

from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.sim_scene import SimScene
from mini_arcade_core.spaces.math.vec2 import Vec2

from asteroids.entities import build_ship
from asteroids.scenes.asteroids.models import (
    AsteroidsTickContext,
    AsteroidsWorld,
)
from asteroids.scenes.asteroids.systems import (
    AsteroidsInputSystem,
    AsteroidsPauseSystem,
    AsteroidsRenderSystem,
    CollisionSystem,
    MotionSystem,
    ShipControlSystem,
    build_asteroids_game_capture_hotkeys_system,
    spawn_asteroid_wave,
)


@register_scene("asteroids")
class AsteroidsScene(SimScene[AsteroidsTickContext, AsteroidsWorld]):
    """
    Main Asteroids gameplay scene.
    """

    tick_context_type = AsteroidsTickContext

    def on_enter(self):
        # Justification: service returns protocol type and static checker
        # does not infer concrete tuple.
        # pylint: disable=assignment-from-no-return
        vw, vh = self.context.services.window.get_virtual_size()
        # pylint: enable=assignment-from-no-return

        ship_pos = Vec2(vw * 0.5, vh * 0.5)
        world = AsteroidsWorld(
            entities=[],
            viewport=(vw, vh),
            score=0,
            lives=3,
            level=1,
            game_over=False,
        )
        world.entities.append(build_ship(x=ship_pos.x, y=ship_pos.y))
        world.entities.extend(
            spawn_asteroid_wave(
                world=world,
                ship_pos=ship_pos,
                level=1,
                count=5,
            )
        )
        self.world = world

        self.systems.extend(
            [
                AsteroidsInputSystem(),
                AsteroidsPauseSystem(),
                build_asteroids_game_capture_hotkeys_system(
                    self.context.services
                ),
                ShipControlSystem(),
                MotionSystem(),
                CollisionSystem(),
                AsteroidsRenderSystem(),
            ]
        )

