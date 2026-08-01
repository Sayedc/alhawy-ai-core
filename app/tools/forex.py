from app.services.market_service import market_service
from app.tools.base import Tool


class ForexTool(Tool):

    SYMBOLS = {
        "usd": "USD",
        "دولار": "USD",

        "eur": "EUR",
        "يورو": "EUR",

        "gbp": "GBP",
        "استرليني": "GBP",

        "egp": "EGP",
        "جنيه": "EGP",
        "مصري": "EGP",
    }

    def __init__(self):
        super().__init__(
            name="forex",
            description="عرض أسعار صرف العملات",
            category="Market",
            version="1.0",
            priority=15,
        )

    @classmethod
    def can_handle(cls, query: str) -> bool:
        text = query.lower()

        for key in cls.SYMBOLS:
            if key in text:
                return True

        return False

    async def run(self, query: str, **kwargs) -> str:
        text = query.lower()

        found = []

        for key, value in self.SYMBOLS.items():
            if key in text and value not in found:
                found.append(value)

        if not found:
            return None

        if len(found) == 1:
            base = found[0]
            target = "EGP" if base != "EGP" else "USD"
        else:
            base = found[0]
            target = found[1]

        data = await market_service.get_forex_rate(base, target)

        if data is None:
            return "❌ تعذر الحصول على سعر الصرف حالياً."

        return (
            f"💱 {data['symbol']}\n\n"
            f"💵 السعر: {data['price']:,.4f} {data['currency']}"
        )
