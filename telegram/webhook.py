from fastapi import APIRouter, Request

from app.telegram.client import TelegramClient

router = APIRouter()

telegram = TelegramClient()


@router.post("/webhook")
async def telegram_webhook(request: Request):
    print("Webhook hit")
    update = await request.json()

    message = update.get("message")

    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        await telegram.send_message(
            chat_id,
            "🚀 Welcome to Alhawy AI Core!\n\nWalking Skeleton is running successfully."
        )

    else:
        await telegram.send_message(
            chat_id,
            f"You said:\n{text}"
        )

    return {"ok": True}
