from typing import Optional

import httpx
import yfinance as yf


class MarketService:
    """
    مسؤول عن جلب بيانات الأسواق المالية.
    """

    CRYPTO_API = "https://api.coingecko.com/api/v3/simple/price"

    async def get_crypto_price(self, coin_id: str) -> Optional[dict]:
        """
        جلب سعر عملة رقمية من CoinGecko.
        """

        try:
            async with httpx.AsyncClient(timeout=20) as client:

                response = await client.get(
                    self.CRYPTO_API,
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

        return {
            "symbol": coin_id.upper(),
            "price": coin.get("usd"),
            "change": coin.get("usd_24h_change", 0),
            "currency": "USD",
            "source": "CoinGecko",
        }

    async def get_gold_price(self) -> Optional[dict]:
        """
        جلب سعر الذهب العالمي.
        """

        try:
            ticker = yf.Ticker("GC=F")

            history = ticker.history(period="2d")

            if history.empty:
                return None

            current = float(history["Close"].iloc[-1])
            previous = float(history["Close"].iloc[-2])

            change = current - previous
            percent = (change / previous) * 100

            return {
                "symbol": "XAU/USD",
                "price": current,
                "change": percent,
                "currency": "USD",
                "source": "Yahoo Finance",
            }

        except Exception:
            return None

    async def get_forex_rate(
        self,
        base: str,
        target: str,
    ) -> Optional[dict]:
        """
        جلب سعر صرف العملات.
        """

        try:
            async with httpx.AsyncClient(timeout=20) as client:

                response = await client.get(
                    "https://api.frankfurter.app/latest",
                    params={
                        "from": base,
                        "to": target,
                    },
                )

                response.raise_for_status()

        except httpx.HTTPError:
            return None

        data = response.json()

        rates = data.get("rates", {})

        if target not in rates:
            return None

        return {
            "symbol": f"{base}/{target}",
            "price": rates[target],
            "currency": target,
            "source": "Frankfurter",
        }


market_service = MarketService()
