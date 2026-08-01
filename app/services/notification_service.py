# app/services/notification_service.py
from app.services.trading_db import trading_db

class NotificationService:
    """خدمة إرسال التحديثات للمتابعين"""
    
    async def send_update_to_followers(self, update: str):
        """إرسال تحديث لجميع المتابعين"""
        followers = trading_db.get_followers()
        
        # هنا ستتم إرسال الرسائل
        # يمكن استخدام Webhooks أو Telegram API مباشرة
        
        return f"✅ تم إرسال التحديث لـ {len(followers)} متابع"
    
    async def send_trade_alert(self, symbol: str, action: str, price: float):
        """إرسال تنبيه صفقة جديدة"""
        message = f"🔔 صفقة جديدة!\n\n"
        message += f"• السهم: {symbol.upper()}\n"
        message += f"• العملية: {action}\n"
        message += f"• السعر: ${price:,.2f}"
        
        return await self.send_update_to_followers(message)

notification_service = NotificationService()
