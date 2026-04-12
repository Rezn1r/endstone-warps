from endstone.plugin import Plugin
from endstone import ColorFormat
from endstone_warps.listener import WarpsListener
from typing_extensions import override

class Warps(Plugin):
    description = "A lightweight warp plugin for Endstone."
    version = "1.0.0"
    api_version = "0.11"
    authors = ["Rezn1r"]

    @override
    def on_load(self) -> None:
        """Called when the plugin is loaded. Use this for pre-setup tasks."""

        self.logger.info(f"{ColorFormat.MATERIAL_EMERALD}Warps{ColorFormat.RESET} is loading... (v{self.version})")
    @override
    def on_enable(self) -> None:
        """Called when the plugin is enabled. Use this for setup."""

        self.save_default_config()
        self.register_events(WarpsListener(self))
        self.logger.info(f"{ColorFormat.MATERIAL_EMERALD}Warps{ColorFormat.RESET} has been enabled! (v{self.version})")

    @override
    def on_disable(self) -> None:
        """Called when the plugin is disabled. Use this for cleanup."""

        self.logger.info(f"{ColorFormat.MATERIAL_EMERALD}Warps{ColorFormat.RESET} has been disabled! (v{self.version})")

