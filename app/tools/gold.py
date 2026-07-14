from app.services.market_service import market_service
from app.tools.base import Tool


class GoldTool(Tool):

    KEYWORDS = [
        "gold",
        "xau",
        "xauusd",
        "ذهب",
        "الذهب",
    ]

    def __init__(self):
        super().__init__(
            name="gold",
            description="عرض سعر الذهب العالمي",
            category="Market",
            version="1.0",
            priority=10,
        )

    @classmethod
    def can_handle(cls, query: str) -> bool:
        text = query.lower()
        return any(keyword in text for keyword in cls.KEYWORDS)

    async def run(self, query: str, **kwargs) -> str:

        data = await market_service.get_gold_price()

        if data is None:
            return None

        trend = "🟢" if data["change"] >= 0 else "🔴"

        return (
            f"🥇 {data['symbol']}\n\n"
            f"💵 السعر: ${data['price']:,.2f}\n"
            f"{trend} التغير: {data['change']:+.2f}%"
        )
