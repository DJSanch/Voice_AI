from plugins.base_plugin import BasePlugin


class TimePlugin(BasePlugin):

    name = "Time Plugin"
    version = "1.0"


    def __init__(self, system_tools):

        self.system_tools = system_tools



    def can_handle(self, command):

        return command.lower() in [
            "time",
            "what time is it",
            "what is the time",
            "tell me the time"
        ]



    def handle(self, command):

        return (
            f"The current time is "
            f"{self.system_tools.get_current_time()}."
        )