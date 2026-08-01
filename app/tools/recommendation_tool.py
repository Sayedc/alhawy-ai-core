# app/tools/recommendation_tool.py
from app.tools.base import Tool
from app.services.trading_db import trading_db


class RecommendationTool(Tool):
    name = "recommendation"
    description = "إدارة التوصيات"

    def can_handle(self, query: str) -> bool:
        keywords = ["توصية", "اقتراح", "نصيحة"]
        return any(k in query.lower() for k in keywords)

    async def run(self, query: str) -> str:
        text = query.lower()

        if "عرض" in text or "جلب" in text:
            return await self.get_recommendations()
        elif "إضافة" in text or "اضف" in text:
            return await self.add_recommendation(text)
        else:
            return "❌ أمر غير معروف للتوصيات"

    async def get_recommendations(self) -> str:
        """جلب التوصيات النشطة"""
        recs = trading_db.get_active_recommendations()

        if not recs:
            return "📭 لا توجد توصيات نشطة حالياً"

        message = "📊 **التوصيات النشطة:**\n\n"
        for rec in recs:
            message += f"""
🔹 **{rec['symbol']}**
   • النوع: {rec['action']}
   • الهدف: ${rec['target_price']}
   • وقف الخسارة: ${rec['stop_loss']}
   • السبب: {rec.get('reason', 'غير محدد')}
   • التاريخ: {rec['date'][:10]}

"""
        return message

    async def add_recommendation(self, text: str) -> str:
        """إضافة توصية جديدة"""
        # هنا هتضيف توصية جديدة
        return "✅ تم إضافة التوصية بنجاح"
