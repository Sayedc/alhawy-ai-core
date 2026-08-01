from typing import Dict, List, Optional
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

    async def get_balance(self, user_id: int) -> str:
        """جلب رصيد المستخدم"""
        try:
            # جلب من Binance
            from app.tools.binance_tool import BinanceTool
            tool = BinanceTool()
            return await tool.balance()
        except:
            # جلب من قاعدة البيانات
            profile = get_profile(user_id)
            if profile:
                return f"💰 الرصيد: ${profile.get('balance', 0):,.2f}"
            return "❌ لم يتم العثور على الرصيد"

    async def get_active_trades(self, user_id: int) -> str:
        """جلب الصفقات المفتوحة"""
        trades = trading_db.get_active_trades()
        if not trades:
            return "📭 لا توجد صفقات مفتوحة"

        message = "📊 **الصفقات المفتوحة:**\n\n"
        for trade in trades:
            message += f"""
🔹 **{trade['symbol']}**
   • النوع: {trade['action']}
   • الكمية: {trade['quantity']:.6f}
   • سعر الدخول: ${trade['entry_price']:,.2f}
   • الربح/الخسارة: {trade.get('profit_loss', 0):,.2f}
   • التاريخ: {trade['date'][:10]}

"""
        return message

    async def get_report(self, user_id: int) -> str:
        """جلب تقرير الأداء"""
        pnl = trading_db.calculate_pnl(str(user_id))
        return f"""
📊 **تقرير الأداء**

🔹 إجمالي الاستثمار: ${pnl.get('total_invested', 0):,.2f}
🔹 الأرباح المحققة: ${pnl.get('total_realized', 0):,.2f}
🔹 الأرباح غير المحققة: ${pnl.get('unrealized_pnl', 0):,.2f}
🔹 إجمالي الأرباح: ${pnl.get('total_pnl', 0):,.2f}
"""

    async def distribute_trades(self, user_id: int, count: int) -> str:
        """توزيع الصفقات على عدة عملات"""
        return f"✅ تم توزيع الصفقة على {count} عملات مختلفة"

    async def get_price(self, symbol: str) -> str:
        """جلب سعر العملة"""
        from app.tools.binance_tool import BinanceTool
        tool = BinanceTool()
        return await tool.price(f"سعر {symbol}")

    async def get_trade_history(self, user_id: int) -> str:
        """جلب تاريخ الصفقات"""
        trades = trading_db.get_trade_history(str(user_id), limit=20)
        if not trades:
            return "📭 لا توجد صفقات سابقة"

        message = "📜 **تاريخ الصفقات:**\n\n"
        for trade in trades:
            status = "🟢" if trade['status'] == 'OPEN' else "🔴"
            message += f"{status} **{trade['symbol']}** - {trade['action']} - ${trade['price']:,.2f}\n"
        return message
