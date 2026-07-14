import yfinance as yf

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
        try:
            ticker = yf.Ticker("GC=F")

            data = ticker.history(period="2d")

            if data.empty:
                return None

            current = float(data["Close"].iloc[-1])

            previous = float(data["Close"].iloc[-2])

            change = current - previous

            percent = (change / previous) * 100

            trend = "🟢" if change >= 0 else "🔴"

            return (
                "🥇 GOLD (XAU/USD)\n\n"
                f"💵 السعر: ${current:,.2f}\n"
                f"{trend} التغير: {change:+.2f} ({percent:+.2f}%)"
            )

        except Exception:
            return None
