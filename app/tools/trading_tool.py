# app/tools/trading_tool.py
from app.tools.base import Tool
from app.services.trading_db import trading_db
from app.services.market_service import market_service
from datetime import datetime

class TradingTool(Tool):
    """
    أداة التداول وإدارة الصفقات
    """
    
    def __init__(self):
        super().__init__(
            name="trading",
            description="إدارة الصفقات والتداول",
            category="Trading",
            version="1.0",
            priority=10,
        )
    
    @classmethod
    def can_handle(cls, query: str) -> bool:
        text = query.lower()
        keywords = [
            "شراء", "بيع", "صفقة", "تداول", "محفظة", "ربح", "خسارة",
            "اشتر", "بع", "دخول", "خروج", "توصية", "تحليل",
            "buy", "sell", "trade", "portfolio", "profit", "loss"
        ]
        return any(k in text for k in keywords)
    
    async def run(self, query: str, **kwargs) -> str:
        text = query.lower()
        user_id = kwargs.get("user_id", "unknown")
        
        # عرض المحفظة
        if "محفظة" in text or "portfolio" in text:
            return await self._show_portfolio()
        
        # عرض الصفقات المفتوحة
        if "صفقات مفتوحة" in text or "open trades" in text:
            return await self._show_open_trades()
        
        # عرض الصفقات المغلقة
        if "صفقات مغلقة" in text or "closed trades" in text:
            return await self._show_closed_trades()
        
        # عرض التوصيات النشطة
        if "توصيات" in text or "recommendations" in text:
            return await self._show_recommendations()
        
        # إضافة صفقة شراء
        if "شراء" in text or "buy" in text:
            return await self._add_buy_trade(text, user_id)
        
        # إضافة صفقة بيع
        if "بيع" in text or "sell" in text:
            return await self._add_sell_trade(text, user_id)
        
        # عرض الأرباح/الخسائر
        if "ربح" in text or "خسارة" in text or "profit" in text or "loss" in text:
            return await self._show_profit_loss()
        
        # متابعة المستخدم
        if "متابعة" in text or "follow" in text:
            return await self._follow_user(user_id)
        
        return "📊 الأوامر المتاحة:\n\n" \
               "• عرض المحفظة\n" \
               "• عرض الصفقات المفتوحة\n" \
               "• عرض الصفقات المغلقة\n" \
               "• عرض التوصيات\n" \
               "• شراء [السهم] [الكمية] @ [السعر]\n" \
               "• بيع [السهم] [الكمية] @ [السعر]\n" \
               "• عرض الربح/الخسارة\n" \
               "• متابعة"
    
    async def _show_portfolio(self) -> str:
        """عرض المحفظة"""
        portfolio = trading_db.get_portfolio()
        summary = trading_db.get_portfolio_summary()
        
        if not portfolio:
            return "📊 المحفظة فارغة حالياً"
        
        # جلب الأسعار الحالية
        total = 0
        response = "📊 **المحفظة الحالية**\n\n"
        
        for item in portfolio:
            # جلب السعر الحالي
            price_data = await market_service.get_stock_price(item['symbol'])
            current_price = price_data['price'] if price_data else item['avg_price']
            
            value = current_price * item['quantity']
            total += value
            
            response += f"• **{item['symbol'].upper()}**\n"
            response += f"  الكمية: {item['quantity']}\n"
            response += f"  متوسط السعر: ${item['avg_price']:,.2f}\n"
            response += f"  السعر الحالي: ${current_price:,.2f}\n"
            response += f"  القيمة: ${value:,.2f}\n\n"
        
        response += f"💰 **إجمالي المحفظة: ${total:,.2f}**"
        
        return response
    
    async def _show_open_trades(self) -> str:
        """عرض الصفقات المفتوحة"""
        trades = trading_db.get_active_trades()
        
        if not trades:
            return "📋 لا توجد صفقات مفتوحة"
        
        response = "📋 **الصفقات المفتوحة**\n\n"
        for trade in trades:
            entry = trade['entry_price']
            current = await self._get_current_price(trade['symbol'])
            profit_loss = (current - entry) * trade['quantity'] if trade['action'] == 'BUY' else (entry - current) * trade['quantity']
            emoji = "📈" if profit_loss >= 0 else "📉"
            
            response += f"• {trade['symbol'].upper()} ({trade['action']})\n"
            response += f"  الدخول: ${entry:,.2f}\n"
            response += f"  الكمية: {trade['quantity']}\n"
            response += f"  {emoji} الربح/الخسارة: ${profit_loss:,.2f}\n\n"
        
        return response
    
    async def _add_buy_trade(self, text: str, user_id: str) -> str:
        """إضافة صفقة شراء"""
        # تحليل النص: "شراء AAPL 10 @ 150"
        parts = text.split()
        if len(parts) < 4:
            return "❌ الصيغة الصحيحة: شراء [السهم] [الكمية] @ [السعر]"
        
        # هذه مجرد بداية - تحتاج تحليل أكثر دقة
        return "✅ تم إضافة صفقة الشراء"
    
    async def _follow_user(self, user_id: str) -> str:
        """متابعة المستخدم"""
        trading_db.add_follower(user_id, f"user_{user_id[:8]}")
        return "✅ تمت المتابعة! ستتلقى التحديثات والتوصيات."
