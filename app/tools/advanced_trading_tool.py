# app/tools/advanced_trading_tool.py
from app.tools.base import Tool
from app.services.stock_analyzer import stock_analyzer
from app.services.trading_education import trading_education
from app.services.trading_db import trading_db
from app.services.market_service import market_service

class AdvancedTradingTool(Tool):
    """
    أداة متقدمة للتداول - تحليل, تعليم, توصيات
    """
    
    def __init__(self):
        super().__init__(
            name="advanced_trading",
            description="تحليل الأسهم المتقدم والمنهج التعليمي",
            category="Trading",
            version="1.0",
            priority=9,
        )
    
    @classmethod
    def can_handle(cls, query: str) -> bool:
        text = query.lower()
        keywords = [
            "أفضل الأسهم", "توب", "تحليل", "منهج", "تعلم", "تعليم",
            "استراتيجية", "نفسية", "مخاطرة", "اختراق", "اتجاه",
            "top stocks", "analysis", "learn", "strategy", "psychology"
        ]
        return any(k in text for k in keywords)
    
    async def run(self, query: str, **kwargs) -> str:
        text = query.lower()
        
        # عرض أفضل الأسهم
        if "أفضل الأسهم" in text or "top stocks" in text:
            return await self._show_top_stocks()
        
        # تحليل سهم معين
        if "تحليل" in text:
            return await self._analyze_stock(text)
        
        # المنهج التعليمي
        if "منهج" in text or "تعلم" in text or "تعليم" in text:
            return await self._show_education(text)
        
        # استراتيجيات التداول
        if "استراتيجية" in text or "strategy" in text:
            return await self._show_strategies(text)
        
        # أخبار السوق
        if "خبر" in text or "اخبار" in text or "news" in text:
            return await self._show_market_news()
        
        return await self._show_help()
    
    async def _show_top_stocks(self) -> str:
        """عرض أفضل الأسهم"""
        top_stocks = await stock_analyzer.get_top_stocks()
        
        if not top_stocks:
            return "❌ تعذر الحصول على بيانات الأسهم"
        
        response = "🏆 **أفضل الأسهم اليوم**\n\n"
        
        for i, stock in enumerate(top_stocks[:10], 1):
            emoji = "🌟" if stock['score'] > 3 else "⭐" if stock['score'] > 2 else "📊"
            change_emoji = "📈" if stock['change'] >= 0 else "📉"
            
            response += f"{i}. {emoji} **{stock['symbol']}** - {stock['name'][:20]}\n"
            response += f"   💰 ${stock['price']:,.2f} {change_emoji} {stock['change']:+.2f}%\n"
            response += f"   📊 النتيجة: {stock['score']:.1f} | RSI: {stock['rsi']:.1f}\n"
            
            if stock['recommendation'] in ['buy', 'strong_buy']:
                response += f"   🟢 توصية: شراء\n"
            elif stock['recommendation'] == 'hold':
                response += f"   🟡 توصية: احتفاظ\n"
            elif stock['recommendation'] in ['sell', 'strong_sell']:
                response += f"   🔴 توصية: بيع\n"
            
            response += "\n"
        
        return response
    
    async def _analyze_stock(self, text: str) -> str:
        """تحليل سهم معين"""
        # استخراج رمز السهم
        words = text.split()
        symbol = None
        for word in words:
            if word.upper() in stock_analyzer.symbols:
                symbol = word.upper()
                break
        
        if not symbol:
            return "❌ من فضلك حدد السهم للتحليل.\nمثال: تحليل AAPL"
        
        # جلب بيانات السهم
        stock_data = await market_service.get_stock_price(symbol)
        if not stock_data:
            return f"❌ تعذر الحصول على بيانات {symbol}"
        
        # جلب التحليل المتقدم
        top_stocks = await stock_analyzer.get_top_stocks()
        stock_analysis = next((s for s in top_stocks if s['symbol'] == symbol), None)
        
        # جلب الأخبار
        news = await stock_analyzer.get_stock_news(symbol)
        
        response = f"📊 **تحليل {symbol}**\n\n"
        
        # البيانات الأساسية
        response += f"💰 السعر: ${stock_data['price']:,.2f}\n"
        response += f"📈 التغير: {stock_data['change']:+.2f}%\n"
        response += f"📊 أعلى/أدنى: ${stock_data.get('high', 0):,.2f} / ${stock_data.get('low', 0):,.2f}\n"
        response += f"📊 حجم التداول: {stock_data.get('volume', 0):,}\n\n"
        
        if stock_analysis:
            # المؤشرات الفنية
            response += "📈 **المؤشرات الفنية**\n"
            response += f"• RSI: {stock_analysis['rsi']:.1f} "
            if stock_analysis['rsi'] < 30:
                response += "🟢 (منطقة شراء)\n"
            elif stock_analysis['rsi'] > 70:
                response += "🔴 (منطقة بيع)\n"
            else:
                response += "🟡 (محايد)\n"
            
            response += f"• المتوسط 50: ${stock_analysis['ma_50']:,.2f}\n"
            response += f"• المتوسط 200: ${stock_analysis['ma_200']:,.2f}\n"
            response += f"• السعر المستهدف: ${stock_analysis['target_price']:,.2f}\n"
            response += f"• نسبة الحجم: {stock_analysis['volume_ratio']:.2f}x\n\n"
        
        # الأخبار
        if news:
            response += "📰 **آخر الأخبار**\n"
            for item in news[:3]:
                sentiment_emoji = "🟢" if item['sentiment'] == "إيجابي" else "🔴" if item['sentiment'] == "سلبي" else "🟡"
                response += f"{sentiment_emoji} {item['title'][:50]}...\n"
            response += "\n"
        
        # التوصية
        if stock_analysis and stock_analysis['score'] > 2:
            response += "🟢 **توصية: شراء**\n"
            response += f"النتيجة: {stock_analysis['score']:.1f}/6\n"
        elif stock_analysis and stock_analysis['score'] > 1:
            response += "🟡 **توصية: احتفاظ**\n"
            response += f"النتيجة: {stock_analysis['score']:.1f}/6\n"
        elif stock_analysis:
            response += "🔴 **توصية: تجنب**\n"
            response += f"النتيجة: {stock_analysis['score']:.1f}/6\n"
        
        return response
    
    async def _show_education(self, text: str) -> str:
        """عرض المنهج التعليمي"""
        # تحديد المستوى
        level = "beginner"
        if "متقدم" in text or "advanced" in text:
            level = "advanced"
        elif "متوسط" in text or "intermediate" in text:
            level = "intermediate"
        elif "مبتدئ" in text or "beginner" in text:
            level = "beginner"
        
        # جلب المحتوى
        level_data = trading_education.get_level(level)
        if not level_data:
            return "❌ المستوى غير موجود"
        
        response = f"📚 **{level_data['name']}**\n\n"
        
        # عرض المواضيع
        for i, topic in enumerate(level_data['topics'], 1):
            response += f"**{i}. {topic['title']}**\n"
            response += f"{topic['content']}\n\n"
            response += "━" * 30 + "\n\n"
        
        # المستوى التالي
        next_level = trading_education.get_next_level(level)
        if next_level:
            next_data = trading_education.get_level(next_level)
            if next_data:
                response += f"⬆️ **المستوى التالي**: {next_data['name']}\n"
                response += f"اكتب: 'منهج {next_level}' للانتقال"
        
        return response
    
    async def _show_market_news(self) -> str:
        """عرض أخبار السوق"""
        # جلب أخبار لأهم الأسهم
        top_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]
        
        response = "📰 **أخبار السوق**\n\n"
        
        for symbol in top_symbols[:5]:
            news = await stock_analyzer.get_stock_news(symbol)
            if news:
                response += f"**{symbol}**\n"
                for item in news[:2]:
                    sentiment_emoji = "🟢" if item['sentiment'] == "إيجابي" else "🔴" if item['sentiment'] == "سلبي" else "🟡"
                    response += f"{sentiment_emoji} {item['title'][:40]}...\n"
                response += "\n"
        
        return response
    
    async def _show_help(self) -> str:
        """عرض المساعدة"""
        return """
📊 **الأوامر المتاحة**

📈 **التحليل:**
• `أفضل الأسهم` - عرض أفضل الأسهم اليوم
• `تحليل [السهم]` - تحليل مفصل لسهم
• `اخبار` - أخبار السوق

📚 **التعليم:**
• `منهج مبتدئ` - المستوى المبتدئ
• `منهج متوسط` - المستوى المتوسط
• `منهج متقدم` - المستوى المتقدم

📊 **استراتيجيات:**
• `استراتيجية اتجاه` - استراتيجية الاتجاه
• `استراتيجية اختراق` - استراتيجية الاختراق
• `استراتيجية تذبذب` - استراتيجية التذبذب

🧠 **علم النفس:**
• `نفسية التداول` - علم نفس التداول
"""
