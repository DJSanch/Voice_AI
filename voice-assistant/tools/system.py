import platform
from datetime import datetime
import subprocess


class SystemTools:

    def get_current_time(self):
        from datetime import datetime
        return datetime.now().strftime("%I:%M %p")


    def open_application(self, app_name: str) -> str:
        try:
            subprocess.run(
                ["open", "-a", app_name],
                check=False
            )

            return f"Opening {app_name}."

        except Exception:
            return f"I couldn't open {app_name}."

    def speak(self, message):
        print(message)
