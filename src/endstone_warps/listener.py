from typing import TYPE_CHECKING

from endstone.event import PlayerMoveEvent, event_handler

if TYPE_CHECKING:
    from endstone_warps.warps import Warps


class WarpsListener:
    def __init__(self, plugin: "Warps") -> None:
        self._plugin = plugin

    @event_handler
    def on_player_move(self, event: PlayerMoveEvent) -> None:
        """Cancel warp countdown if player moves (X, Y, Z only, not looking around)."""
        player = event.player
        if player.name not in self._plugin.warping_players:
            return

        warp_data = self._plugin.warping_players[player.name]
        start_x, start_y, start_z = warp_data["start_pos"]
        current_x, current_y, current_z = player.location.x, player.location.y, player.location.z

        # Check if player moved (ignoring yaw and pitch)
        if (start_x, start_y, start_z) != (current_x, current_y, current_z):
            # Player moved, cancel the warp
            self._plugin._cancel_warp(player)