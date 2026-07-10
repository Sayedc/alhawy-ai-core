import httpx

from app.config.settings import settings
from app.providers.base import AIProvider


class GeminiProvider(AIProvider):

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                params={"key": settings.GEMINI_API_KEY},
                json={
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt}
                            ]
                        }
                    ]
                },
            )

            print(response.status_code)
            print(response.text)

            response.raise_for_status()

            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
