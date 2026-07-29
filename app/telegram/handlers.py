from app.telegram.client import TelegramClient

telegram = TelegramClient()


async def handle_update(update: dict):

    message = update.get("message")

    if not message:
        return

    chat = message.get("chat", {})

    chat_id = chat.get("id")

    text = message.get("text", "")

    if not chat_id:
        return

    await telegram.send_message(
        chat_id,
        f"استلمت رسالتك:\n\n{text}"
    )
