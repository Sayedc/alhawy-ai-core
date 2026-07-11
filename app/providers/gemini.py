import httpx

from app.config.settings import settings
from app.providers.base import AIProvider
from app.memory.memory import add_message, get_history
from app.memory.profile import get_profile


class GeminiProvider(AIProvider):

    async def generate(self, user_id: int, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            # جلب التاريخ من الذاكرة
            history = get_history(user_id)

            # جلب الملف الشخصي للمستخدم
            profile = get_profile(user_id)

            # بناء contents من الذاكرة
            contents = []

            # إضافة الملف الشخصي كأول رسالة إذا كان موجود
            if profile:
                profile_text = f"""
User Profile

Name: {profile['name']}
Favorite Market: {profile['favorite_market']}
Capital: {profile['capital']}
Risk Level: {profile['risk_level']}
Summary: {profile['summary']}
"""
                contents.insert(
                    0,
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": profile_text
                            }
                        ]
                    }
                )

            # إضافة التاريخ من الذاكرة
            for msg in history:
                contents.append(
                    {
                        "role": msg["role"],
                        "parts": [
                            {
                                "text": msg["text"]
                            }
                        ]
                    }
                )

            # إضافة الرسالة الحالية
            contents.append(
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            )

            response = await client.post(
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
                    "contents": contents
                },
            )

            print("Status:", response.status_code)
            print("Response:", response.text)

            response.raise_for_status()

            data = response.json()
            answer = data["candidates"][0]["content"]["parts"][0]["text"]

            # حفظ الرسائل في الذاكرة
            add_message(user_id, "user", prompt)
            add_message(user_id, "model", answer)

            return answer
