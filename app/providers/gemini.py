import httpx

from app.config.settings import settings
from app.providers.base import AIProvider
from app.memory.memory import add_message, get_history
from app.memory.profile import get_profile, save_profile
from app.memory.extractor import extract_profile
from app.tools.router import ToolRouter


class GeminiProvider(AIProvider):

    def __init__(self):
        self.tool_router = ToolRouter()

    async def generate(self, user_id: int, prompt: str) -> str:
        # تشغيل الأدوات أولاً
        tool_result = await self.tool_router.run(prompt)

        if tool_result is not None:
            # حفظ الرسالة والرد في الذاكرة
            add_message(user_id, "user", prompt)
            add_message(user_id, "model", tool_result)
            return tool_result

        async with httpx.AsyncClient(timeout=30) as client:
            # جلب التاريخ من الذاكرة
            history = get_history(user_id)

            # جلب الملف الشخصي للمستخدم
            profile = get_profile(user_id)

            # بناء الـ profile text
            profile_text = ""
            if profile:
                profile_text = f"""
User Profile

Name: {profile.get('name')}
Favorite Market: {profile.get('favorite_market')}
Capital: {profile.get('capital')}
Risk: {profile.get('risk_level')}
Summary: {profile.get('summary')}
"""

            # بناء contents من الذاكرة
            contents = []

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
                                "text": f"""
أنت Alhawy Trading AI.

{profile_text}

أنت متخصص في التداول والفوركس والعملات الرقمية والأسهم.

إذا عرفت معلومات عن المستخدم فاستخدمها أثناء الحديث.

لا تخترع أسعارًا أو أخبارًا.

أي تحليل هو لغرض تعليمي فقط.
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

            # استخراج وحفظ الملف الشخصي من الرسالة
            try:
                info = await extract_profile(prompt)

                if info:
                    current = profile or {}

                    save_profile(
                        user_id=user_id,
                        name=info.get("name") or current.get("name"),
                        favorite_market=info.get("favorite_market") or current.get("favorite_market"),
                        capital=info.get("capital") or current.get("capital"),
                        risk_level=info.get("risk_level") or current.get("risk_level"),
                        summary=info.get("summary") or current.get("summary"),
                    )

            except Exception:
                pass

            return answer
