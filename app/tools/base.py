from abc import ABC, abstractmethod


class Tool(ABC):

    name: str
    description: str

    @abstractmethod
    async def run(self, query: str):
        pass

    @abstractmethod
    def can_handle(self, query: str) -> bool:
        pass
