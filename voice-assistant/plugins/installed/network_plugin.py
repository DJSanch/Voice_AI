from plugins.base_plugin import BasePlugin


class NetworkPlugin(BasePlugin):

    name = "Network Awareness Plugin"
    version = "1.0"
    description = "Scans network devices"


    def __init__(self, network):

        self.network = network



    def can_handle(self, command):

        text = command.lower()


        return any(
            phrase in text
            for phrase in [
                "network status",
                "show network devices",
                "who is connected"
            ]
        )



    def handle(self, command):

        return self.network.network_report()