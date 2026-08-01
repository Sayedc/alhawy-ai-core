from app.tools.base import Tool


class StocksTool(Tool):

    def __init__(self):
        super().__init__(
            name="stocks",
            description="Stocks Tool",
            category="Stocks",
            priority=50,
        )

    @classmethod
    def can_handle(cls, query: str) -> bool:
        return False

    async def run(self, query: str, **kwargs) -> str:
        return None
