from typing import List, Dict
from app.config.settings import settings
from app.services.trading_db import trading_db


class RiskManager:
    """إدارة المخاطر"""

    def __init__(self):
        self.consecutive_losses = 0
        self.consecutive_wins = 0

    async def filter_signals(self, signals: List[Dict]) -> List[Dict]:
        """فلترة الإشارات حسب المخاطر"""
        if not signals:
            return []

        filtered = []

        for signal in signals:
            # 1. تصفية حسب نسبة النجاح
            if signal.get('confidence', 0) < 70:
                continue

            # 2. تصفية حسب المخاطر
            risk_score = await self.calculate_risk_score(signal)
            if risk_score > 0.6:
                continue

            filtered.append(signal)

        return filtered

    async def calculate_risk_score(self, signal: Dict) -> float:
        """حساب درجة المخاطرة"""
        score = 0.0

        # نسبة النجاح
        confidence = signal.get('confidence', 0)
        if confidence < 70:
            score += 0.3
        elif confidence < 80:
            score += 0.2

        # نسبة الخسارة
        loss_percent = signal.get('loss_percent', 0)
        if loss_percent > 2:
            score += 0.3
        elif loss_percent > 1.5:
            score += 0.2

        # الخسائر المتتالية
        if self.consecutive_losses >= 3:
            score += 0.4

        return score

    async def calculate_position_size(self, user_id: int, signal: Dict) -> float:
        """حساب حجم الصفقة"""
        # جلب رصيد المستخدم
        profile = trading_db.get_user_profile(user_id)
        if not profile:
            return settings.DEFAULT_TRADE_AMOUNT

        balance = profile.get('balance', 1000)
        risk_percent = profile.get('risk_percent', settings.DEFAULT_RISK_PERCENT)

        # حساب حجم الصفقة
        risk_amount = balance * (risk_percent / 100)
        position_size = risk_amount / (signal.get('loss_percent', 1) / 100)

        # تقليل الحجم في حالة الخسائر المتتالية
        if self.consecutive_losses >= 3:
            position_size *= 0.5

        # زيادة الحجم في حالة المكاسب المتتالية
        if self.consecutive_wins >= 3:
            position_size *= 1.2

        # الحد الأقصى
        max_size = balance * 0.5
        return min(position_size, max_size)

    async def update_sequence(self, is_win: bool):
        """تحديث سلسلة المكاسب والخسائر"""
        if is_win:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
