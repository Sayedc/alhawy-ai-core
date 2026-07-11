import httpx

from app.tools.base import Tool


class CryptoTool(Tool):

    name = "crypto"

    description = "Get cryptocurrency prices"

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

    async def run(self, query: str):

        text = query.lower()

        coin_id = None

        for key, value in self.COINS.items():
            if key in text:
                coin_id = value
                break

        if coin_id is None:
            return None

        async with httpx.AsyncClient(timeout=20) as client:

            response = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                },
            )

        if response.status_code != 200:
            return None

        data = response.json()

        if coin_id not in data:
            return None

        price = data[coin_id]["usd"]
        change = data[coin_id].get("usd_24h_change", 0)

        return (
            f"💰 {coin_id.upper()}\n\n"
            f"السعر الحالي: ${price:,.2f}\n"
            f"تغير 24 ساعة: {change:.2f}%"
      )
