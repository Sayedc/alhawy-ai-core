import httpx

from app.config.settings import settings


class TelegramClient:
    BASE_URL = "https://api.telegram.org"

    def __init__(self):
        self.token = settings.BOT_TOKEN

    async def send_message(self, chat_id: int, text: str):
        url = f"{self.BASE_URL}/bot{self.token}/sendMessage"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": text,
                },
            )

        response.raise_for_status()
        return response.json()
