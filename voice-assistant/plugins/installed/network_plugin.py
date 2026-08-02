from plugins.base_plugin import BasePlugin
from services.dashboard import update_dashboard_state


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

        report = self.network.network_report()
        update_dashboard_state(
            status="active",
            mode="network",
            activity="Network devices displayed",
            last_command=command,
            last_response=report,
            details={
                "network_panel": True,
                "network_devices": self.network.last_network_report,
            },
        )
        return report