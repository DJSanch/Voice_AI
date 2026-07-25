import platform
from datetime import datetime


class SystemTools:
    def get_system_info(self) -> str:
        return platform.platform()

    def get_current_time(self) -> str:
        return datetime.now().strftime("%I:%M %p")

    def get_current_date(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")
