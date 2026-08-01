from app.tools.base import Tool


class NewsTool(Tool):

    def __init__(self):
        super().__init__(
            name="news",
            description="News Tool",
            category="News",
            priority=50,
        )

    @classmethod
    def can_handle(cls, query: str) -> bool:
        return False

    async def run(self, query: str, **kwargs) -> str:
        return None
