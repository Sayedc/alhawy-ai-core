# app/tools/binance_tool.py
from app.tools.base import Tool
from binance.client import Client
from binance.exceptions import BinanceAPIException
from app.config.settings import settings
from app.services.trading_db import trading_db


class BinanceTool(Tool):
    name = "binance"
    description = "تنفيذ أوامر شراء وبيع على Binance"

    def __init__(self):
        self.client = Client(
            settings.BINANCE_API_KEY,
            settings.BINANCE_SECRET_KEY,
            testnet=settings.BINANCE_TESTNET
        )

    def can_handle(self, query: str) -> bool:
        keywords = ["اشتري", "بيع", "رصيد", "سعر", "شراء", "بيع"]
        return any(k in query.lower() for k in keywords)

    async def run(self, query: str) -> str:
        text = query.lower()

        if "اشتري" in text or "شراء" in text:
            return await self.buy(text)
        elif "بيع" in text:
            return await self.sell(text)
        elif "رصيد" in text:
            return await self.balance()
        elif "سعر" in text:
            return await self.price(text)
        else:
            return "❌ الأمر غير معروف"

    async def buy(self, text: str) -> str:
        try:
            # استخراج المبلغ والعملة
            symbol, amount = await self._parse_order(text)

            # جلب السعر الحالي
            price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
            quantity = amount / price

            # تنفيذ الأمر
            order = self.client.order_market_buy(
                symbol=symbol,
                quantity=quantity
            )

            # حفظ في قاعدة البيانات
            trade_result = trading_db.execute_buy_order(
                symbol=symbol,
                quantity=quantity,
                price=price,
                user_id=None
            )

            return f"""
✅ **تم الشراء بنجاح!**

🔹 العملة: {symbol}
🔹 الكمية: {quantity:.6f}
🔹 السعر: ${price:,.2f}
🔹 المبلغ: ${amount:,.2f}
🔹 رقم الصفقة: {order['orderId']}
"""

        except BinanceAPIException as e:
            return f"❌ فشل الشراء: {e.message}"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"

    async def sell(self, text: str) -> str:
        try:
            symbol, amount = await self._parse_order(text)

            # جلب السعر الحالي
            price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
            quantity = amount / price

            # تنفيذ الأمر
            order = self.client.order_market_sell(
                symbol=symbol,
                quantity=quantity
            )

            # حفظ في قاعدة البيانات
            trade_result = trading_db.execute_sell_order(
                symbol=symbol,
                quantity=quantity,
                price=price,
                user_id=None
            )

            return f"""
✅ **تم البيع بنجاح!**

🔹 العملة: {symbol}
🔹 الكمية: {quantity:.6f}
🔹 السعر: ${price:,.2f}
🔹 المبلغ: ${amount:,.2f}
🔹 رقم الصفقة: {order['orderId']}
"""

        except BinanceAPIException as e:
            return f"❌ فشل البيع: {e.message}"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"

    async def balance(self) -> str:
        try:
            account = self.client.get_account()
            balances = account['balances']

            message = "💰 **الرصيد:**\n\n"
            for bal in balances:
                free = float(bal['free'])
                locked = float(bal['locked'])
                if free > 0 or locked > 0:
                    message += f"🔹 {bal['asset']}: {free:.6f} (محجوز: {locked:.6f})\n"

            return message
        except Exception as e:
            return f"❌ خطأ في جلب الرصيد: {str(e)}"

    async def price(self, text: str) -> str:
        try:
            # استخراج العملة
            import re
            match = re.search(r'([A-Za-z]+)', text)
            if not match:
                return "❌ لم يتم تحديد العملة"

            symbol = match.group(1).upper() + "USDT"

            # جلب السعر
            price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])

            # جلب التغير
            stats = self.client.get_ticker(symbol=symbol)

            return f"""
📊 **سعر {symbol}**

🔹 السعر الحالي: ${price:,.2f}
🔹 التغير 24 ساعة: {stats.get('priceChangePercent', '0')}%
🔹 أعلى سعر: ${stats.get('highPrice', '0')}
🔹 أدنى سعر: ${stats.get('lowPrice', '0')}
🔹 حجم التداول: {stats.get('volume', '0')}
"""

        except Exception as e:
            return f"❌ خطأ في جلب السعر: {str(e)}"

    async def _parse_order(self, text: str) -> tuple:
        """استخراج العملة والمبلغ من النص"""
        import re

        # استخراج العملة
        symbol = "BTCUSDT"
        if "BTC" in text.upper() or "بيتكوين" in text:
            symbol = "BTCUSDT"
        elif "ETH" in text.upper() or "ايثريوم" in text:
            symbol = "ETHUSDT"
        elif "SOL" in text.upper() or "سولانا" in text:
            symbol = "SOLUSDT"
        elif "BNB" in text.upper() or "بينانس" in text:
            symbol = "BNBUSDT"

        # استخراج المبلغ
        amount = 100.0
        match = re.search(r'(\d+)', text)
        if match:
            amount = float(match.group(1))

        return symbol, amount
