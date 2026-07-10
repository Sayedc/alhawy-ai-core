from fastapi import APIRouter, Request

from app.providers import AIManager
from app.telegram.client import TelegramClient

router = APIRouter()

telegram = TelegramClient()
ai = AIManager()


@router.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()

    message = update.get("message")

    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    try:
        if text == "/start":
            reply = (
                "🚀 أهلاً بك في Alhawy AI\n\n"
                "أنا جاهز لمساعدتك.\n"
                "اكتب أي سؤال أو اطلب تحليل."
            )
        else:
            reply = await ai.generate(text)

    except Exception as e:
        reply = f"⚠️ حدث خطأ:\n{str(e)}"

    await telegram.send_message(chat_id, reply)

    return {"ok": True}
