# app/tools/recommendation_tool.py
from app.tools.base import Tool
from app.services.trading_db import trading_db
from app.services.market_service import market_service

class RecommendationTool(Tool):
    """
    أداة التوصيات والتحليل
    """
    
    def __init__(self):
        super().__init__(
            name="recommendations",
            description="توصيات التداول والتحليل",
            category="Trading",
            version="1.0",
            priority=8,
        )
    
    @classmethod
    def can_handle(cls, query: str) -> bool:
        text = query.lower()
        keywords = ["توصية", "انصح", "اشتري", "بيع", "احتفظ", "stop loss", "target"]
        return any(k in text for k in keywords)
    
    async def run(self, query: str, **kwargs) -> str:
        text = query.lower()
        
        # عرض التوصيات النشطة
        if "نشطة" in text or "active" in text:
            return await self._show_active_recommendations()
        
        # إضافة توصية جديدة (للمسؤولين فقط)
        if "أضف توصية" in text:
            return await self._add_recommendation(text)
        
        # تحليل سهم معين
        return await self._analyze_stock(text)
    
    async def _analyze_stock(self, text: str) -> str:
        """تحليل سهم معين"""
        # تحديد السهم من النص
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]
        symbol = None
        for s in symbols:
            if s.lower() in text:
                symbol = s
                break
        
        if not symbol:
            return "❌ من فضلك حدد السهم للتحليل.\nمثال: تحليل AAPL"
        
        # جلب بيانات السهم
        stock_data = await market_service.get_stock_price(symbol)
        if not stock_data:
            return f"❌ تعذر الحصول على بيانات {symbol}"
        
        # جلب التوصيات من السوق
        # (هذا يحتاج API متقدم)
        
        response = f"📊 **تحليل {symbol.upper()}**\n\n"
        response += f"💰 السعر: ${stock_data['price']:,.2f}\n"
        response += f"📈 التغير: {stock_data['change']:+.2f}%\n\n"
        
        # تحليل سريع
        if stock_data['change'] > 2:
            response += "📈 **توصية: شراء**\n"
            response += "السهم في اتجاه صاعد قوي"
        elif stock_data['change'] < -2:
            response += "📉 **توصية: بيع**\n"
            response += "السهم في اتجاه هابط"
        else:
            response += "🟡 **توصية: احتفاظ**\n"
            response += "السهم في حالة استقرار"
        
        return response
