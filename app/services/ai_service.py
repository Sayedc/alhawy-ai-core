from app.providers.manager import AIManager


class AIService:

    def __init__(self):
        self.ai = AIManager()

    async def chat(self, user_id: int, message: str) -> str:
        """
        إرسال رسالة إلى الذكاء الاصطناعي وإرجاع الرد.
        """
        return await self.ai.generate(user_id, message)


ai_service = AIService()
