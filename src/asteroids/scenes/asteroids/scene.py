"""
Playable Asteroids scene.
"""

from __future__ import annotations

from dataclasses import replace

from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.bootstrap import (
    scene_entities_config,
    scene_viewport,
)
from mini_arcade_core.scenes.game_scene import (
    GameScene,
    GameSceneSystemsConfig,
)

from asteroids.scenes.asteroids.bootstrap import build_asteroids_world
from asteroids.scenes.asteroids.models import (
    AsteroidsIntent,
    AsteroidsTickContext,
    AsteroidsWorld,
)
from asteroids.scenes.asteroids.pipeline import build_asteroids_systems
from asteroids.scenes.asteroids.systems import AsteroidsRenderSystem
from asteroids.scenes.commands import PauseAsteroidsCommand


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


@register_scene("asteroids")
class AsteroidsScene(GameScene[AsteroidsTickContext, AsteroidsWorld]):
    """
    Main Asteroids gameplay scene.
    """

    tick_context_type = AsteroidsTickContext
    capture_config = replace(
        GameScene.capture_config,
        replay_game_id="asteroids",
    )
    systems_config = GameSceneSystemsConfig(
        controls_scene_key="asteroids",
        intent_factory=_build_asteroids_intent,
        input_system_name="asteroids_input",
        pause_command_factory=lambda _ctx: PauseAsteroidsCommand(),
        render_system_factory=lambda _runtime: AsteroidsRenderSystem(),
    )

    def debug_overlay_lines(self) -> list[str]:
        ship = self.world.ship()
        lines = [
            f"score: {self.world.score}",
            f"lives: {self.world.lives}",
            f"level: {self.world.level}",
            f"asteroids: {len(self.world.asteroids())}",
            f"bullets: {len(self.world.bullets())}",
            f"game_over: {self.world.game_over}",
        ]
        if ship is not None:
            lines.extend(
                [
                    (
                        "ship_pos: "
                        f"({ship.transform.center.x:.1f},"
                        f" {ship.transform.center.y:.1f})"
                    ),
                    (
                        (
                            "ship_vel: "
                            f"({ship.kinematic.velocity.x:.1f},"
                            f" {ship.kinematic.velocity.y:.1f})"
                        )
                        if ship.kinematic is not None
                        else "ship_vel: (n/a)"
                    ),
                    f"ship_rot: {ship.rotation_deg:.1f}",
                    f"ship_invuln: {getattr(ship, 'invuln_timer', 0.0):.2f}",
                ]
            )
        return lines

    def on_enter(self):
        viewport = scene_viewport(self)
        entities_cfg = scene_entities_config(
            self,
            error_message="Missing gameplay.scenes.asteroids.entities config",
        )
        self.world = build_asteroids_world(
            viewport=viewport,
            entities_cfg=entities_cfg,
        )

        self.systems.extend(build_asteroids_systems())
