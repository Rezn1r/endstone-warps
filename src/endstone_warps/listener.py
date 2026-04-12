from endstone.plugin import Plugin

class WarpsListener:
    def __init__(self, plugin: Plugin) -> None:
        self._plugin = plugin