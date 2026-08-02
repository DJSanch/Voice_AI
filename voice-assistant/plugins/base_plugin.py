from abc import ABC, abstractmethod


class BasePlugin(ABC):

    name = "Unknown Plugin"
    version = "1.0"
    description = "No description available"


    @abstractmethod
    def can_handle(self, command: str) -> bool:
        pass


    @abstractmethod
    def handle(self, command: str) -> str:
        pass