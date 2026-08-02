from plugins.base_plugin import BasePlugin


class PluginInfoPlugin(BasePlugin):

    name = "Plugin Info"
    version = "1.0"
    description = "Shows installed Astra plugins"


    def __init__(self, manager):

        self.manager = manager



    def can_handle(self, command):

        return (
            "list plugins" in command.lower()
            or
            "show plugins" in command.lower()
        )



    def handle(self, command):

        return self.manager.list_plugins()