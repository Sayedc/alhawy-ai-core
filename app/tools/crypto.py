import httpx

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

        try:
            async with httpx.AsyncClient(timeout=20) as client:

                response = await client.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params={
                        "ids": coin_id,
                        "vs_currencies": "usd",
                        "include_24hr_change": "true",
                    },
                )

                response.raise_for_status()

        except httpx.HTTPError:
            return None

        data = response.json()

        if coin_id not in data:
            return None

        coin = data[coin_id]

        price = coin.get("usd")
        change = coin.get("usd_24h_change", 0)

        if price is None:
            return None

        trend = "🟢" if change >= 0 else "🔴"

        return (
            f"🪙 {coin_id.upper()}\n\n"
            f"💵 السعر الحالي: ${price:,.2f}\n"
            f"{trend} تغير 24 ساعة: {change:.2f}%"
        )
