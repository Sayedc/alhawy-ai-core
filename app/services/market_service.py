# app/services/market_service.py
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

    async def get_forex_rate(self, base: str, target: str):
        """
        جلب سعر صرف العملات.
        """

        url = f"https://open.er-api.com/v6/latest/{base}"

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url)
            response.raise_for_status()

        data = response.json()

        if data["result"] != "success":
            return None

        rate = data["rates"].get(target)

        if rate is None:
            return None

        return {
            "symbol": f"{base}/{target}",
            "price": rate,
            "currency": target,
            "source": "ExchangeRate API",
        }

    async def get_stock_price(self, symbol: str) -> Optional[dict]:
        """
        جلب سعر سهم حقيقي من Yahoo Finance
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # جلب السعر الحالي
            data = ticker.history(period="1d")
            if data.empty:
                return None
            
            current_price = float(data['Close'].iloc[-1])
            
            # جلب معلومات إضافية
            info = ticker.info
            
            # حساب التغير
            prev_close = info.get('previousClose', current_price)
            change = ((current_price - prev_close) / prev_close) * 100
            
            return {
                "symbol": symbol.upper(),
                "price": current_price,
                "change": change,
                "high": float(data['High'].iloc[-1]),
                "low": float(data['Low'].iloc[-1]),
                "volume": int(data['Volume'].iloc[-1]),
                "name": info.get('longName', symbol.upper()),
                "currency": info.get('currency', 'USD'),
                "source": "Yahoo Finance"
            }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

    async def get_multiple_stocks(self, symbols: list) -> dict:
        """
        جلب أسعار عدة أسهم في وقت واحد
        """
        results = {}
        for symbol in symbols:
            data = await self.get_stock_price(symbol)
            if data:
                results[symbol] = data
        return results

market_service = MarketService()
