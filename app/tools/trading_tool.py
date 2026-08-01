# app/tools/trading_tool.py (الكود الكامل)

from app.tools.base import Tool
from app.services.trading_db import trading_db
from app.services.market_service import market_service
import re

class TradingTool(Tool):
    """
    أداة التداول - تنفيذ صفقات حقيقية
    """
    
    def __init__(self):
        super().__init__(
            name="trading",
            description="تنفيذ صفقات التداول وإدارة المحفظة",
            category="Trading",
            version="1.0",
            priority=10,
        )
    
    @classmethod
    def can_handle(cls, query: str) -> bool:
        text = query.lower()
        keywords = [
            "شراء", "بيع", "صفقة", "تداول", "محفظة", "ربح", "خسارة",
            "اشتر", "بع", "دخول", "خروج", "buy", "sell", "trade"
        ]
        return any(k in text for k in keywords)
    
    async def run(self, query: str, **kwargs) -> str:
        text = query.lower()
        user_id = kwargs.get("user_id", "default_user")
        
        # عرض المحفظة
        if "محفظة" in text or "portfolio" in text:
            return await self._show_portfolio(user_id)
        
        # عرض الصفقات
        if "صفقات" in text or "trades" in text:
            return await self._show_trades(user_id)
        
        # عرض الأرباح
        if "ربح" in text or "خسارة" in text or "pnl" in text:
            return await self._show_pnl(user_id)
        
        # شراء
        if "شراء" in text or "buy" in text:
            return await self._execute_buy(text, user_id)
        
        # بيع
        if "بيع" in text or "sell" in text:
            return await self._execute_sell(text, user_id)
        
        return await self._show_help()
    
    async def _execute_buy(self, text: str, user_id: str) -> str:
        """تنفيذ أمر شراء"""
        # تحليل النص: "شراء AAPL 100 @ 150"
        pattern = r"شراء\s+(\w+)\s+(\d+)\s*@?\s*([\d.]+)"
        match = re.search(pattern, text)
        
        if not match:
            return "❌ الصيغة الصحيحة: شراء [السهم] [الكمية] @ [السعر]\nمثال: شراء AAPL 100 @ 150"
        
        symbol = match.group(1).upper()
        quantity = int(match.group(2))
        price = float(match.group(3))
        
        # التحقق من السعر الحقيقي (اختياري)
        real_price = await market_service.get_stock_price(symbol)
        if real_price:
            current_price = real_price['price']
            # تحذير إذا كان السعر مختلف
            if abs(current_price - price) / current_price > 0.05:  # فرق 5%
                return f"⚠️ السعر الحقيقي لـ {symbol} هو ${current_price:,.2f}\n" \
                       f"هل أنت متأكد من السعر ${price:,.2f}؟"
        
        # تنفيذ الصفقة
        result = trading_db.execute_buy_order(symbol, quantity, price, user_id)
        
        if "error" in result:
            return f"❌ {result['error']}"
        
        return f"✅ **تم تنفيذ صفقة شراء**\n\n" \
               f"• السهم: {symbol}\n" \
               f"• الكمية: {quantity}\n" \
               f"• السعر: ${price:,.2f}\n" \
               f"• الإجمالي: ${quantity * price:,.2f}\n" \
               f"• رقم الصفقة: #{result['trade_id']}"
    
    async def _execute_sell(self, text: str, user_id: str) -> str:
        """تنفيذ أمر بيع"""
        pattern = r"بيع\s+(\w+)\s+(\d+)\s*@?\s*([\d.]+)"
        match = re.search(pattern, text)
        
        if not match:
            return "❌ الصيغة الصحيحة: بيع [السهم] [الكمية] @ [السعر]\nمثال: بيع AAPL 100 @ 155"
        
        symbol = match.group(1).upper()
        quantity = int(match.group(2))
        price = float(match.group(3))
        
        result = trading_db.execute_sell_order(symbol, quantity, price, user_id)
        
        if "error" in result:
            return f"❌ {result['error']}"
        
        return f"✅ **تم تنفيذ صفقة بيع**\n\n" \
               f"• السهم: {symbol}\n" \
               f"• الكمية: {quantity}\n" \
               f"• السعر: ${price:,.2f}\n" \
               f"• الإجمالي: ${quantity * price:,.2f}\n" \
               f"• رقم الصفقة: #{result['trade_id']}"
    
    async def _show_portfolio(self, user_id: str) -> str:
        """عرض المحفظة"""
        portfolio = trading_db.get_portfolio()
        
        if not portfolio:
            return "📊 المحفظة فارغة"
        
        response = "📊 **المحفظة الحالية**\n\n"
        total_value = 0
        
        for item in portfolio:
            # جلب السعر الحالي
            stock = await market_service.get_stock_price(item['symbol'])
            current_price = stock['price'] if stock else item['avg_price']
            
            value = current_price * item['quantity']
            total_value += value
            
            profit_loss = (current_price - item['avg_price']) * item['quantity']
            emoji = "📈" if profit_loss >= 0 else "📉"
            
            response += f"• **{item['symbol']}**\n"
            response += f"  الكمية: {item['quantity']}\n"
            response += f"  السعر الحالي: ${current_price:,.2f}\n"
            response += f"  القيمة: ${value:,.2f}\n"
            response += f"  {emoji} ربح/خسارة: ${profit_loss:,.2f}\n\n"
        
        response += f"💰 **إجمالي المحفظة: ${total_value:,.2f}**"
        
        return response
    
    async def _show_trades(self, user_id: str) -> str:
        """عرض الصفقات"""
        trades = trading_db.get_trade_history(user_id, limit=10)
        
        if not trades:
            return "📋 لا توجد صفقات"
        
        response = "📋 **آخر الصفقات**\n\n"
        for trade in trades[:10]:
            action_emoji = "🟢" if trade['action'] == 'BUY' else "🔴"
            response += f"{action_emoji} **{trade['action']}** {trade['symbol']}\n"
            response += f"  الكمية: {trade['quantity']} @ ${trade['price']:,.2f}\n"
            response += f"  الإجمالي: ${trade['total']:,.2f}\n"
            response += f"  الحالة: {trade['status']}\n\n"
        
        return response
    
    async def _show_pnl(self, user_id: str) -> str:
        """عرض الأرباح والخسائر"""
        pnl = trading_db.calculate_pnl(user_id)
        
        return f"📊 **ملخص الأرباح والخسائر**\n\n" \
               f"💰 إجمالي المستثمر: ${pnl['total_invested']:,.2f}\n" \
               f"💰 الأرباح المحققة: ${pnl['realized_pnl']:,.2f}\n" \
               f"📈 الأرباح غير المحققة: ${pnl['unrealized_pnl']:,.2f}\n" \
               f"💵 إجمالي الأرباح: ${pnl['total_pnl']:,.2f}"
    
    async def _show_help(self) -> str:
        """عرض المساعدة"""
        return "📊 **أوامر التداول المتاحة**\n\n" \
               "• **شراء [السهم] [الكمية] @ [السعر]**\n" \
               "  مثال: شراء AAPL 100 @ 150\n\n" \
               "• **بيع [السهم] [الكمية] @ [السعر]**\n" \
               "  مثال: بيع AAPL 100 @ 155\n\n" \
               "• **عرض المحفظة** - عرض أسهمك\n" \
               "• **عرض الصفقات** - عرض تاريخ الصفقات\n" \
               "• **عرض الربح/الخسارة** - عرض الأرباح"
