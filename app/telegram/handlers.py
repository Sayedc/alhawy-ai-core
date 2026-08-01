from app.services.ai_service import ai_service
from app.telegram.client import TelegramClient

telegram = TelegramClient()


async def handle_update(update: dict):

    message = update.get("message")

    if not message:
        return

    chat = message.get("chat", {})

    chat_id = chat.get("id")

    text = message.get("text", "")

    if not chat_id or not text:
        return

    try:
        reply = await ai_service.chat(chat_id, text)

    except Exception as e:
        reply = f"حدث خطأ:\n{e}"

    await telegram.send_message(chat_id, reply)
