"""
Scene-level commands for Asteroids.
"""

from __future__ import annotations

from mini_arcade_core.engine.commands import (
    ChangeSceneCommand,
    Command,
    CommandContext,
    PushSceneIfMissingCommand,
    RemoveSceneCommand,
)
from mini_arcade_core.engine.scenes.models import ScenePolicy


class StartAsteroidsCommand(Command):
    """Switch from menu to gameplay scene."""

    def execute(self, context: CommandContext):
        ChangeSceneCommand("asteroids").execute(context)


class PauseAsteroidsCommand(Command):
    """Push pause overlay scene."""

    def execute(self, context: CommandContext):
        PushSceneIfMissingCommand(
            "asteroids_pause",
            as_overlay=True,
            policy=ScenePolicy(
                blocks_update=True,
                blocks_input=True,
                is_opaque=False,
                receives_input=True,
            ),
        ).execute(context)


class ResumeAsteroidsCommand(Command):
    """Remove pause overlay scene."""

    def execute(self, context: CommandContext):
        RemoveSceneCommand("asteroids_pause").execute(context)


class RestartAsteroidsCommand(Command):
    """Restart gameplay from scratch."""

    def execute(self, context: CommandContext):
        ChangeSceneCommand("asteroids").execute(context)


class BackToMenuCommand(Command):
    """Return to game main menu."""

    def execute(self, context: CommandContext):
        ChangeSceneCommand("asteroids_menu").execute(context)
