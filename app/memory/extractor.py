import json

import httpx

from app.config.settings import settings


SYSTEM_PROMPT = """
أنت نظام لاستخراج بيانات المستخدم.

استخرج فقط إذا كانت موجودة.

أرجع JSON فقط بدون أي كلام.

{
    "name": null,
    "favorite_market": null,
    "capital": null,
    "risk_level": null,
    "summary": null
}
"""


async def extract_profile(text: str):
    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent",
            params={"key": settings.GEMINI_API_KEY},
            json={
                "system_instruction": {
                    "parts": [
                        {
                            "text": SYSTEM_PROMPT
                        }
                    ]
                },
                "contents": [
                    {
                        "parts": [
                            {
                                "text": text
                            }
                        ]
                    }
                ]
            },
        )

        response.raise_for_status()

        answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]

        answer = answer.replace("```json", "").replace("```", "").strip()

        return json.loads(answer)
