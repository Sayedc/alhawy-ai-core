from abc import ABC, abstractmethod


class Tool(ABC):
    name: str
    description: str
    version: str = "1.0"
    category: str
    enabled: bool = True
    priority: int = 100

    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        version: str = "1.0",
        enabled: bool = True,
        priority: int = 100
    ):
        self.name = name
        self.description = description
        self.category = category
        self.version = version
        self.enabled = enabled
        self.priority = priority

    @abstractmethod
    async def run(self, query: str, **kwargs) -> str:
        pass

    @classmethod
    @abstractmethod
    def can_handle(cls, query: str) -> bool:
        pass

    def is_available(self) -> bool:
        return self.enabled

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "enabled": self.enabled,
            "priority": self.priority,
            "type": self.__class__.__name__
        }
