# app/trading/bot_engine.py
import asyncio
from datetime import datetime
from typing import Optional, Dict, List

from app.config.settings import settings
from app.services.market_service import market_service
from app.services.trading_db import trading_db
from app.trading.strategy import StrategyManager
from app.trading.risk_manager import RiskManager
from app.trading.trade_manager import TradeManager
from app.telegram.client import TelegramClient
from app.memory.profile import get_profile


class BotEngine:
    """المحرك الرئيسي للتداول الآلي"""

    def __init__(self):
        self.telegram = TelegramClient()
        self.strategy_manager = StrategyManager()
        self.risk_manager = RiskManager()
        self.trade_manager = TradeManager()
        self.is_running = False
        self.active_signals = {}  # user_id -> signal

    async def start(self):
        """بدء تشغيل المحرك"""
        self.is_running = True
        await self.telegram.broadcast("🚀 بدأ تشغيل محرك التداول الآلي")

    async def stop(self):
        """إيقاف المحرك"""
        self.is_running = False
        await self.telegram.broadcast("⏹️ تم إيقاف محرك التداول الآلي")

    async def scan_markets(self):
        """مسح الأسواق وتحليلها"""
        while self.is_running:
            try:
                # 1. تحليل السوق
                signals = await self.strategy_manager.analyze_all_markets()

                # 2. تقييم المخاطر
                filtered_signals = await self.risk_manager.filter_signals(signals)

                # 3. إرسال الإشارات للمستخدمين
                await self.send_signals(filtered_signals)

                # 4. تحديث الصفقات المفتوحة
                await self.trade_manager.update_open_trades()

                # 5. انتظار الدورة التالية
                await asyncio.sleep(settings.SCAN_INTERVAL_MINUTES * 60)

            except Exception as e:
                await self.telegram.broadcast(f"❌ خطأ في المسح: {str(e)}")
                await asyncio.sleep(60)

    async def send_signals(self, signals: List[Dict]):
        """إرسال الإشارات للمستخدمين"""
        # جلب المستخدمين النشطين
        users = trading_db.get_followers()

        for user in users:
            user_id = user['user_id']

            # جلب الملف الشخصي للمستخدم
            profile = get_profile(user_id)
            amount = profile.get('trade_amount', settings.DEFAULT_TRADE_AMOUNT) if profile else settings.DEFAULT_TRADE_AMOUNT

            # اختيار أفضل إشارة للمستخدم
            best_signal = await self.select_best_signal(signals, user_id)

            if best_signal:
                # حفظ الإشارة للمستخدم
                self.active_signals[user_id] = best_signal

                # إرسال الإشعار
                message = self.format_signal_message(best_signal, amount)
                await self.telegram.send_message(user_id, message)

    def format_signal_message(self, signal: Dict, amount: float) -> str:
        """تنسيق رسالة الإشارة"""
        return f"""
📊 **صفقة مقترحة جديدة!**

📍 السوق: {signal.get('market', 'غير معروف')}
🔹 العملة: {signal.get('symbol', 'غير معروف')}
🔹 النوع: {signal.get('action', 'غير معروف')}
🔹 السعر الحالي: ${signal.get('price', 0):,.2f}
🔹 الهدف: ${signal.get('target', 0):,.2f} ({signal.get('profit_percent', 0):.1f}%)
🔹 وقف الخسارة: ${signal.get('stop_loss', 0):,.2f} ({signal.get('loss_percent', 0):.1f}%)
🔹 نسبة النجاح: {signal.get('confidence', 0)}%
🔹 المبلغ المقترح: ${amount:,.2f}

📌 **السبب**: {signal.get('reason', 'تحليل فني')}

⚠️ تحليل تعليمي وليس نصيحة استثمارية

💬 **توافق على تنفيذ الصفقة؟** (نعم / لا)
"""

    async def execute_signal(self, user_id: int, signal: Dict) -> str:
        """تنفيذ إشارة"""
        result = await self.trade_manager.execute_trade(user_id, signal)
        self.active_signals.pop(user_id, None)
        return result

    async def select_best_signal(self, signals: List[Dict], user_id: int) -> Optional[Dict]:
        """اختيار أفضل إشارة للمستخدم"""
        if not signals:
            return None

        # ترتيب حسب نسبة النجاح
        sorted_signals = sorted(signals, key=lambda x: x.get('confidence', 0), reverse=True)
        return sorted_signals[0] if sorted_signals else None
