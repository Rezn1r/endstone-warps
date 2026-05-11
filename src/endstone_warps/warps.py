from math import ceil
from time import time

from endstone import ColorFormat, Player
from endstone.command import Command, CommandSender
from endstone.plugin import Plugin
from endstone.level import Location
from endstone_warps.database import (
    delete_warp,
    get_warp,
    initialize_database,
    list_warps,
    save_warp,
)
from endstone_warps.listener import WarpsListener
from sqlalchemy.engine import Engine
from typing_extensions import override


class Warps(Plugin):
    description = "A lightweight warp plugin for Endstone."
    version = "1.0.4"
    api_version = "0.11"
    authors = ["Rezn1r"]

    def __init__(self) -> None:
        super().__init__()
        self._database_engine: Engine | None = None
        self.warping_players: dict[str, dict] = {}  # Tracks players in warp countdown
        self.player_cooldowns: dict[str, float] = {}  # Tracks warp cooldown per player

    # Commands
    commands = {
        "warp": {
            "description": "Teleport to a warp point.",
            "usages": ["/warp <name: string>", "/wp <name: string>"],
            "aliases": ["wp"],
            "permissions": ["warps.use"],
        },
        "setwarp": {
            "description": "Set a warp point at your current location.",
            "usages": ["/setwarp <name: string>"],
            "permissions": ["warps.set"],
        },
        "delwarp": {
            "description": "Delete a warp point.",
            "usages": ["/delwarp <name: string>"],
            "permissions": ["warps.delete"],
        },
        "warps": {
            "description": "List all warp points.",
            "usages": ["/warps [page: int]"],
            "permissions": ["warps.list"],
        },
    }

    # Permissions
    permissions = {
        "warps.use": {
            "description": "Allows the player to use warps.",
            "default": True,
        },
        "warps.set": {
            "description": "Allows the player to set warps.",
            "default": True,
        },
        "warps.delete": {
            "description": "Allows the player to delete warps.",
            "default": True,
        },
        "warps.list": {
            "description": "Allows the player to list warps.",
            "default": True,
        },
        "warps.admin": {
            "description": "Grants all warps permissions.",
            "default": False,
        },
    }

    @override
    def on_load(self) -> None:
        """Called when the plugin is loaded. Use this for pre-setup tasks."""

        self._database_engine = initialize_database(self.data_folder)
        self.logger.info(
            f"{ColorFormat.MATERIAL_EMERALD}Warps{ColorFormat.RESET} is loading... (v{self.version})"
        )

    @override
    def on_enable(self) -> None:
        """Called when the plugin is enabled. Use this for setup."""

        self.save_default_config()
        self.register_events(WarpsListener(self))

        # Start countdown ticker (runs every 20 ticks = 1 second)
        self.server.scheduler.run_task(
            self, self._tick_warp_countdowns, delay=20, period=20
        )

        self.logger.info(
            f"{ColorFormat.MATERIAL_EMERALD}Warps{ColorFormat.RESET} has been enabled! (v{self.version})"
        )

    @override
    def on_disable(self) -> None:
        """Called when the plugin is disabled. Use this for cleanup."""

        if self._database_engine is not None:
            self._database_engine.dispose()
            self._database_engine = None
        self.logger.info(
            f"{ColorFormat.MATERIAL_EMERALD}Warps{ColorFormat.RESET} has been disabled! (v{self.version})"
        )

    def on_command(
        self, sender: CommandSender, command: Command, args: list[str]
    ) -> bool:
        match command.name:
            case "setwarp":
                return self._handle_setwarp(sender, args)
            case "warp":
                return self._handle_warp(sender, args)
            case "delwarp":
                return self._handle_delwarp(sender, args)
            case "warps":
                return self._handle_listwarps(sender, args)
        return False

    def _database(self) -> Engine:
        if self._database_engine is None:
            raise RuntimeError("Database is not initialized.")
        return self._database_engine

    def _normalize_warp_name(self, name: str) -> str:
        return name.strip().lower()

    def _handle_setwarp(self, sender: CommandSender, args: list[str]) -> bool:
        if not isinstance(sender, Player):
            sender.send_message(
                f"{ColorFormat.RED}Only players can set warps.{ColorFormat.RESET}"
            )
            return True

        if len(args) != 1:
            sender.send_message(
                f"{ColorFormat.RED}Usage: /setwarp <name>{ColorFormat.RESET}"
            )
            return True

        warp_name = self._normalize_warp_name(args[0])
        if not warp_name:
            sender.send_message(
                f"{ColorFormat.RED}Warp name cannot be empty.{ColorFormat.RESET}"
            )
            return True

        location = sender.location
        save_warp(
            self._database(),
            warp_name,
            sender.dimension.name,
            location.x,
            location.y,
            location.z,
            location.yaw,
            location.pitch,
            sender.name,
            int(time()),
        )
        sender.send_message(
            f"{ColorFormat.GREEN}Warp '{warp_name}' set.{ColorFormat.RESET}"
        )
        return True

    def _handle_warp(self, sender: CommandSender, args: list[str]) -> bool:
        if not isinstance(sender, Player):
            sender.send_message(
                f"{ColorFormat.RED}Only players can use warps.{ColorFormat.RESET}"
            )
            return True

        if len(args) != 1:
            sender.send_message(
                f"{ColorFormat.RED}Usage: /warp <name>{ColorFormat.RESET}"
            )
            return True

        # Check cooldown
        cooldown_seconds = self.config.get("warp", {}).get("cooldown_seconds", 5)
        current_time = time()
        player_name = sender.name

        if player_name in self.player_cooldowns:
            time_left = cooldown_seconds - (
                current_time - self.player_cooldowns[player_name]
            )
            if time_left > 0:
                sender.send_message(
                    f"{ColorFormat.RED}You must wait {time_left:.1f}s before warping again.{ColorFormat.RESET}"
                )
                return True

        warp_name = self._normalize_warp_name(args[0])
        warp = get_warp(self._database(), warp_name)
        if warp is None:
            sender.send_message(
                f"{ColorFormat.RED}Warp '{warp_name}' was not found.{ColorFormat.RESET}"
            )
            return True

        dimension = sender.dimension.level.get_dimension(str(warp["world"]))
        location = Location(
            dimension,
            float(warp["x"]),
            float(warp["y"]),
            float(warp["z"]),
            float(warp["pitch"] or 0),
            float(warp["yaw"] or 0),
        )

        # Start warp countdown
        self._start_warp_countdown(sender, location, warp_name)
        sender.send_message(
            f"{ColorFormat.YELLOW}Warp in progress... don't move!{ColorFormat.RESET}"
        )
        return True

    def _handle_delwarp(self, sender: CommandSender, args: list[str]) -> bool:
        if len(args) != 1:
            sender.send_message(
                f"{ColorFormat.RED}Usage: /delwarp <name>{ColorFormat.RESET}"
            )
            return True

        warp_name = self._normalize_warp_name(args[0])
        if not delete_warp(self._database(), warp_name):
            sender.send_message(
                f"{ColorFormat.RED}Warp '{warp_name}' was not found.{ColorFormat.RESET}"
            )
            return True

        sender.send_message(
            f"{ColorFormat.GREEN}Warp '{warp_name}' deleted.{ColorFormat.RESET}"
        )
        return True

    def _handle_listwarps(self, sender: CommandSender, args: list[str]) -> bool:
        if len(args) > 1:
            sender.send_message(
                f"{ColorFormat.RED}Usage: /warps [page]{ColorFormat.RESET}"
            )
            return True

        page = 1
        if args:
            try:
                page = max(1, int(args[0]))
            except ValueError:
                sender.send_message(
                    f"{ColorFormat.RED}Page must be a number.{ColorFormat.RESET}"
                )
                return True

        rows = list_warps(self._database())
        if not rows:
            sender.send_message(
                f"{ColorFormat.YELLOW}No warps have been set yet.{ColorFormat.RESET}"
            )
            return True

        page_size = 10
        total_pages = max(1, ceil(len(rows) / page_size))
        if page > total_pages:
            sender.send_message(
                f"{ColorFormat.RED}Page {page} does not exist. There are {total_pages} pages.{ColorFormat.RESET}"
            )
            return True

        start = (page - 1) * page_size
        end = start + page_size
        lines = []
        for row in rows[start:end]:
            lines.append(
                f"{ColorFormat.YELLOW}{row['uuid']}{ColorFormat.RESET} - {row['world']} ({row['x']:.2f}, {row['y']:.2f}, {row['z']:.2f})"
            )

        sender.send_message(
            f"{ColorFormat.MATERIAL_EMERALD}Warps{ColorFormat.RESET} page {page}/{total_pages}:"
        )
        for line in lines:
            sender.send_message(line)
        return True

    def _start_warp_countdown(
        self, player: Player, location: Location, warp_name: str
    ) -> None:
        """Start a countdown before warping."""
        countdown_duration = self.config.get("warp", {}).get("countdown_duration", 3)
        player_name = player.name
        self.warping_players[player_name] = {
            "location": location,
            "warp_name": warp_name,
            "countdown": countdown_duration,
            "start_pos": (player.location.x, player.location.y, player.location.z),
        }

    def _tick_warp_countdowns(self) -> None:
        """Process all active warp countdowns. Called every second by scheduler."""
        # Make a copy of keys to avoid dict changing size during iteration
        for player_name in list(self.warping_players.keys()):
            if player_name not in self.warping_players:
                continue

            warp_data = self.warping_players[player_name]
            player = self.server.get_player(player_name)
            if player is None:
                # Player logged off, cancel warp
                self.warping_players.pop(player_name, None)
                continue

            countdown = warp_data["countdown"]

            # Play sound
            player.play_sound(player.location, "mob.shulker.teleport")

            # Update tip
            if countdown > 0:
                player.send_tip(
                    f"{ColorFormat.AQUA}Warping in {countdown}s... {ColorFormat.RESET}"
                )

            # Decrement countdown
            warp_data["countdown"] -= 1

            # If countdown reaches 0, perform the warp
            if warp_data["countdown"] < 0:
                self._complete_warp(player)

    def _complete_warp(self, player: Player) -> None:
        """Complete the warp and teleport the player."""
        player_name = player.name
        if player_name not in self.warping_players:
            return

        warp_data = self.warping_players.pop(player_name)
        location = warp_data["location"]
        warp_name = warp_data["warp_name"]

        # Create a new location with warp destination but player's current yaw/pitch
        teleport_location = Location(
            location.dimension,
            location.x,
            location.y,
            location.z,
            player.location.pitch,
            player.location.yaw,
        )

        if not player.teleport(teleport_location):
            player.send_message(
                f"{ColorFormat.RED}Failed to teleport to '{warp_name}'.{ColorFormat.RESET}"
            )
            return

        # Set cooldown
        self.player_cooldowns[player_name] = time()

        player.send_message(
            f"{ColorFormat.GREEN}Teleported to '{warp_name}'.{ColorFormat.RESET}"
        )
        player.send_tip(f"{ColorFormat.GREEN}Warped!{ColorFormat.RESET}")

    def _cancel_warp(self, player: Player) -> None:
        """Cancel an active warp and deal damage."""
        player_name = player.name
        if player_name not in self.warping_players:
            return

        self.warping_players.pop(player_name)
        player.send_message(f"{ColorFormat.RED}Warp cancelled!{ColorFormat.RESET}")
        player.send_tip(f"{ColorFormat.RED}Warp cancelled!{ColorFormat.RESET}")
