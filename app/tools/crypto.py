from app.services.market_service import market_service
from app.tools.base import Tool


class CryptoTool(Tool):

    COINS = {
        "bitcoin": "bitcoin",
        "btc": "bitcoin",
        "بيتكوين": "bitcoin",

        "ethereum": "ethereum",
        "eth": "ethereum",
        "ايثريوم": "ethereum",

        "solana": "solana",
        "سولانا": "solana",

        "bnb": "binancecoin",
        "بينانس": "binancecoin",
    }

    def __init__(self):
        super().__init__(
            name="crypto",
            description="عرض أسعار العملات الرقمية",
            category="Market",
            version="1.0",
            priority=20,
        )

    @classmethod
    def can_handle(cls, query: str) -> bool:
        text = query.lower()
        return any(key in text for key in cls.COINS)

    async def run(self, query: str, **kwargs) -> str:

        text = query.lower()

        coin_id = None

        for key, value in self.COINS.items():
            if key in text:
                coin_id = value
                break

        if coin_id is None:
            return None

        data = await market_service.get_crypto_price(coin_id)

        if data is None:
            return None

        trend = "🟢" if data["change"] >= 0 else "🔴"

        return (
            f"🪙 {data['symbol']}\n\n"
            f"💵 السعر: ${data['price']:,.2f}\n"
            f"{trend} التغير: {data['change']:.2f}%"
        )
