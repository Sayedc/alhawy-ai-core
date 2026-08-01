from typing import Dict, List
from datetime import datetime
from app.services.trading_db import trading_db
from app.trading.risk_manager import RiskManager
from app.telegram.client import TelegramClient
from app.config.settings import settings


class TradeManager:
    """إدارة الصفقات"""

    def __init__(self):
        self.risk_manager = RiskManager()
        self.telegram = TelegramClient()

    async def execute_trade(self, user_id: int, signal: Dict) -> str:
        """تنفيذ صفقة"""
        try:
            # 1. حساب حجم الصفقة
            quantity = await self.risk_manager.calculate_position_size(user_id, signal)

            # 2. حساب الكمية
            amount = quantity / signal['price']

            # 3. تنفيذ الشراء/البيع
            if signal['action'] == 'BUY':
                result = trading_db.execute_buy_order(
                    symbol=signal['symbol'],
                    quantity=amount,
                    price=signal['price'],
                    user_id=str(user_id)
                )
            else:
                result = trading_db.execute_sell_order(
                    symbol=signal['symbol'],
                    quantity=amount,
                    price=signal['price'],
                    user_id=str(user_id)
                )

            if 'error' in result:
                return f"❌ {result['error']}"

            # 4. حفظ الصفقة
            trade_id = result['trade_id']

            # 5. إرسال إشعار
            message = f"""
✅ **تم تنفيذ الصفقة بنجاح!**

🔹 العملة: {signal['symbol']}
🔹 النوع: {signal['action']}
🔹 الكمية: {amount:.6f}
🔹 سعر الدخول: ${signal['price']:,.2f}
🔹 الهدف: ${signal['target']:,.2f}
🔹 وقف الخسارة: ${signal['stop_loss']:,.2f}
🔹 المبلغ: ${quantity:,.2f}
🔹 نسبة النجاح: {signal['confidence']}%

📌 سيتم متابعة الصفقة تلقائياً.
"""

            await self.telegram.send_message(user_id, message)
            return message

        except Exception as e:
            return f"❌ فشل التنفيذ: {str(e)}"

    async def update_open_trades(self):
        """تحديث الصفقات المفتوحة"""
        active_trades = trading_db.get_active_trades()

        for trade in active_trades:
            # جلب السعر الحالي
            current_price = await self._get_current_price(trade['symbol'])

            if not current_price:
                continue

            # حساب الربح/الخسارة
            profit = (current_price - trade['entry_price']) / trade['entry_price'] * 100
            profit_amount = (current_price - trade['entry_price']) * trade['quantity']

            # التحقق من الهدف
            if profit >= settings.DEFAULT_TAKE_PROFIT:
                await self.close_trade(trade['id'], current_price, "الهدف")

            # التحقق من وقف الخسارة
            elif profit <= -settings.DEFAULT_STOP_LOSS:
                await self.close_trade(trade['id'], current_price, "وقف الخسارة")

    async def close_trade(self, trade_id: int, price: float, reason: str):
        """إغلاق صفقة"""
        result = trading_db.close_trade(trade_id, price)

        if result:
            # جلب بيانات الصفقة
            trade = trading_db.get_trade(trade_id)
            if trade:
                message = f"""
✅ **تم إغلاق الصفقة!**

🔹 العملة: {trade['symbol']}
🔹 السبب: {reason}
🔹 سعر الدخول: ${trade['entry_price']:,.2f}
🔹 سعر الخروج: ${price:,.2f}
🔹 الربح/الخسارة: {trade['profit_loss']:,.2f} ({trade['profit_loss_percent']:.2f}%)
"""

                await self.telegram.send_message(trade['user_id'], message)

    async def _get_current_price(self, symbol: str) -> float:
        """جلب السعر الحالي"""
        # هنا هتجيب السعر من MarketService
        # حالياً مؤقت
        return 0.0
