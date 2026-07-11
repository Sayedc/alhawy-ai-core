import httpx

from app.config.settings import settings
from app.providers.base import AIProvider


class GeminiProvider(AIProvider):

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                # ✅ استخدام الموديل الأحدث والأكثر توافقًا
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent",
                params={"key": settings.GEMINI_API_KEY},
                json={
                    "system_instruction": {
                        "parts": [
                            {
                                "text": """
أنت Alhawy Trading AI.

أنت مساعد ذكاء اصطناعي متخصص في:
- التداول
- الفوركس
- العملات الرقمية
- الأسهم
- التحليل الفني
- التحليل الأساسي

تعطي إجابات احترافية ومنظمة.

إذا لم تكن متأكدًا من معلومة فقل ذلك بوضوح.

لا تخترع بيانات أسعار أو أخبار.

إذا طُلب منك تحليل سوق، اذكر أن التحليل تعليمي وليس نصيحة استثمارية.
"""
                            }
                        ]
                    },
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt}
                            ]
                        }
                    ]
                },
            )

            print("Status:", response.status_code)
            print("Response:", response.text)

            response.raise_for_status()

            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
