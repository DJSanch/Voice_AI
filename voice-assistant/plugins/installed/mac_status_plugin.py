from plugins.base_plugin import BasePlugin


class MacStatusPlugin(BasePlugin):

    name = "Mac Status Plugin"
    version = "1.0"
    description = "Monitors MacBook resources"


    def __init__(self, mac_status):

        self.mac_status = mac_status



    def can_handle(self, command):

        text = command.lower()


        return any(
            phrase in text
            for phrase in [
                "mac status",
                "check my mac",
                "system status",
                "computer status",
                "cpu",
                "ram",
                "memory",
                "storage",
                "battery"
            ]
        )



    def handle(self, command):

        text = command.lower()


        if (
            "mac status" in text
            or "check my mac" in text
            or "system status" in text
        ):

            return self.mac_status.full_status()



        if "cpu" in text:

            return self.mac_status.cpu_usage()



        if (
            "memory" in text
            or "ram" in text
        ):

            return self.mac_status.memory_usage()



        if (
            "storage" in text
            or "disk" in text
        ):

            return self.mac_status.disk_space()



        if "battery health" in text:

            return self.mac_status.battery_health()



        return self.mac_status.battery()