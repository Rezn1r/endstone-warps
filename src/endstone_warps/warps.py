from endstone.plugin import Plugin
from endstone import ColorFormat
from endstone_warps.database import initialize_database
from endstone_warps.listener import WarpsListener
from sqlalchemy.engine import Engine
from typing_extensions import override

class Warps(Plugin):
    
    description = "A lightweight warp plugin for Endstone."
    version = "1.0.0"
    api_version = "0.11"
    authors = ["Rezn1r"]

    def __init__(self) -> None:
        super().__init__()
        self._database_engine: Engine | None = None

    # Commands
    commands = {
        "warp": {
            "description": "Teleport to a warp point.",
            "usage": "/warp <name: string>",
            "permission": "warps.use",
        },
        "setwarp": {
            "description": "Set a warp point at your current location.",
            "usage": "/setwarp <name: string>",
            "permission": "warps.set",
        },
        "delwarp": {
            "description": "Delete a warp point.",
            "usage": "/delwarp <name: string>",
            "permission": "warps.delete",
        },
        "warps": {
            "description": "List all warp points.",
            "usage": "/warps [page: int]",
            "permission": "warps.list",
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

        if self._database_engine is not None:
            self._database_engine.dispose()
            self._database_engine = None
        self.logger.info(f"{ColorFormat.MATERIAL_EMERALD}Warps{ColorFormat.RESET} has been disabled! (v{self.version})")

