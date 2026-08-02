from plugins.base_plugin import BasePlugin
from services.dashboard import update_dashboard_state


class SecurityPlugin(BasePlugin):

    name = "Security Awareness Plugin"
    version = "1.0"
    description = "Analyzes network security"


    def __init__(self, security):

        self.security = security



    def can_handle(self, command):

        text = command.lower()


        return (
            "security report" in text
            or
            "security status" in text
            or
            "check security" in text
            or
            "scan security" in text
        )



    def handle(self, command):

        text = command.lower()


        if (
            "security report" in text
            or "security status" in text
        ):

            return self.security.security_report()



        new_devices = (
            self.security.scan_security()
        )


        if not new_devices:
            response = (
                "Security scan complete. No new devices detected."
            )
        else:
            response = "New devices detected:\n"
            for device in new_devices:
                response += (
                    f"{device['vendor']} "
                    f"at {device['ip']}.\n"
                )

        update_dashboard_state(
            status="active",
            mode="security",
            activity="Security scan displayed",
            last_command=command,
            last_response=response,
            details={"security_panel": True},
        )

        return response


        for device in new_devices:

            response += (
                f"{device['vendor']} "
                f"at {device['ip']}.\n"
            )


        return response