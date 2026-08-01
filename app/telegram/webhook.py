# app/telegram/webhook.py (إضافة الأوامر الجديدة)
from fastapi import APIRouter, Request
from app.providers import AIManager
from app.telegram.client import TelegramClient
from app.trading.bot_engine import BotEngine
from app.services.trading_db import trading_db
from app.memory.profile import get_profile, save_profile
from app.config.settings import settings

router = APIRouter()
telegram = TelegramClient()
ai = AIManager()
bot_engine = BotEngine()

# تخزين الصفقات المعلقة
pending_trades = {}


@router.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    message = update.get("message")

    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    # ====== 1. التعامل مع موافقة/رفض الصفقة ======
    if chat_id in pending_trades:
        signal = pending_trades[chat_id]

        if "نعم" in text or "تمام" in text or "yes" in text.lower():
            result = await bot_engine.trade_manager.execute_trade(chat_id, signal)
            await telegram.send_message(chat_id, result)
            del pending_trades[chat_id]

        elif "لا" in text or "مش" in text or "no" in text.lower():
            await telegram.send_message(chat_id, "❌ تم إلغاء الصفقة")
            del pending_trades[chat_id]

        else:
            await telegram.send_message(chat_id, "❓ أجب بـ **نعم** أو **لا**")

        return {"ok": True}

    # ====== 2. أوامر التداول ======

    if text == "/start":
        reply = """
🚀 **أهلاً بك في Alhawy Trading AI!**

📋 **الأوامر المتاحة:**

🔹 `تفعيل` - بدء البحث عن صفقات
🔹 `إيقاف` - إيقاف البحث
🔹 `رصيدي` - عرض الرصيد
🔹 `صفقاتي` - عرض الصفقات المفتوحة
🔹 `تحديد مبلغ 200$` - تغيير مبلغ التداول
🔹 `تحديد مخاطرة 2%` - تغيير نسبة المخاطرة
🔹 `تقرير` - عرض ملخص الأداء
🔹 `استراتيجية RSI` - تغيير الاستراتيجية
🔹 `توزيع 3` - توزيع الصفقات على 3 عملات
🔹 `نبهني BTC 60000` - تنبيه عند سعر معين
🔹 `سعر BTC` - جلب السعر الحالي
🔹 `ذاكرتي` - عرض تاريخ الصفقات

💡 **أسئلة عادية:** اسألني أي حاجة عن التداول!
"""

    elif "تفعيل" in text:
        if not bot_engine.is_running:
            await bot_engine.start()
            reply = "✅ بدأ تشغيل محرك التداول الآلي"
        else:
            reply = "⚠️ المحرك يعمل بالفعل"

    elif "إيقاف" in text:
        if bot_engine.is_running:
            await bot_engine.stop()
            reply = "⏹️ تم إيقاف محرك التداول الآلي"
        else:
            reply = "⚠️ المحرك متوقف بالفعل"

    elif "رصيدي" in text:
        reply = await bot_engine.trade_manager.get_balance(chat_id)

    elif "صفقاتي" in text:
        reply = await bot_engine.trade_manager.get_active_trades(chat_id)

    elif "تحديد مبلغ" in text:
        import re
        match = re.search(r'(\d+)', text)
        if match:
            amount = float(match.group(1))
            save_profile(chat_id, trade_amount=amount)
            reply = f"✅ تم تحديد مبلغ التداول: ${amount:,.2f}"
        else:
            reply = "❌ يرجى تحديد المبلغ (مثال: `تحديد مبلغ 200$`)"

    elif "تحديد مخاطرة" in text:
        import re
        match = re.search(r'(\d+)', text)
        if match:
            risk = float(match.group(1))
            save_profile(chat_id, risk_percent=risk)
            reply = f"✅ تم تحديد نسبة المخاطرة: {risk}%"
        else:
            reply = "❌ يرجى تحديد النسبة (مثال: `تحديد مخاطرة 2%`)"

    elif "تقرير" in text:
        reply = await bot_engine.trade_manager.get_report(chat_id)

    elif "استراتيجية" in text:
        if "RSI" in text.upper():
            bot_engine.strategy_manager.set_strategy("rsi")
            reply = "✅ تم تغيير الاستراتيجية إلى: RSI"
        elif "MACD" in text.upper():
            bot_engine.strategy_manager.set_strategy("macd")
            reply = "✅ تم تغيير الاستراتيجية إلى: MACD"
        elif "بولينجر" in text:
            bot_engine.strategy_manager.set_strategy("bollinger")
            reply = "✅ تم تغيير الاستراتيجية إلى: بولينجر باند"
        else:
            strategies = bot_engine.strategy_manager.get_strategies()
            reply = f"""
📊 **الاستراتيجيات المتاحة:**

{"".join([f"🔹 `{key}`: {value}\n" for key, value in strategies.items()])}

مثال: `استراتيجية RSI`
"""

    elif "توزيع" in text:
        import re
        match = re.search(r'(\d+)', text)
        if match:
            count = int(match.group(1))
            reply = await bot_engine.trade_manager.distribute_trades(chat_id, count)
        else:
            reply = "❌ يرجى تحديد عدد العملات (مثال: `توزيع 3`)"

    elif "نبهني" in text:
        import re
        match = re.search(r'([A-Za-z]+)\s*(\d+)', text)
        if match:
            symbol = match.group(1).upper()
            price = float(match.group(2))
            # هنا هتضيف التنبيه في قاعدة البيانات
            reply = f"✅ تم تفعيل التنبيه لـ {symbol} عند سعر ${price:,.2f}"
        else:
            reply = "❌ يرجى تحديد العملة والسعر (مثال: `نبهني BTC 60000`)"

    elif "سعر" in text:
        import re
        match = re.search(r'([A-Za-z]+)', text)
        if match:
            symbol = match.group(1).upper()
            reply = await bot_engine.trade_manager.get_price(symbol)
        else:
            reply = "❌ يرجى تحديد العملة (مثال: `سعر BTC`)"

    elif "ذاكرتي" in text:
        reply = await bot_engine.trade_manager.get_trade_history(chat_id)

    else:
        # ====== 3. الأسئلة العادية (AI) ======
        reply = await ai.generate(chat_id, text)

    await telegram.send_message(chat_id, reply)
    return {"ok": True}
