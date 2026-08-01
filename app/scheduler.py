from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.trading.bot_engine import BotEngine
from app.services.trading_db import trading_db


class Scheduler:
    """المجدول الزمني"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.bot_engine = BotEngine()

    async def start(self):
        """بدء المجدول"""
        # 1. مسح الأسواق كل X دقائق
        self.scheduler.add_job(
            self.bot_engine.scan_markets,
            IntervalTrigger(minutes=5),
            id="scan_markets"
        )

        # 2. تحديث الصفقات كل دقيقة
        self.scheduler.add_job(
            self.bot_engine.trade_manager.update_open_trades,
            IntervalTrigger(minutes=1),
            id="update_trades"
        )

        # 3. تقرير يومي الساعة 12:00
        self.scheduler.add_job(
            self._send_daily_report,
            CronTrigger(hour=12, minute=0),
            id="daily_report"
        )

        self.scheduler.start()

    async def stop(self):
        """إيقاف المجدول"""
        self.scheduler.shutdown()

    async def _send_daily_report(self):
        """إرسال تقرير يومي"""
        # جلب المستخدمين
        users = trading_db.get_followers()
        for user in users:
            # حساب الأداء اليومي
            report = self._calculate_daily_report(user['user_id'])
            await self.bot_engine.telegram.send_message(user['user_id'], report)

    def _calculate_daily_report(self, user_id: str) -> str:
        """حساب التقرير اليومي"""
        # هنا هنحسب الأداء اليومي
        return """
📊 **تقرير اليوم**

الصفقات المنفذة: 0
الصفقات الرابحة: 0
الصفقات الخاسرة: 0
إجمالي الربح: $0
"""


# إنشاء كائن واحد
scheduler = Scheduler()
