from app.providers.gemini import GeminiProvider


class AIManager:
    def __init__(self):
        self.provider = GeminiProvider()

    async def generate(self, user_id: int, prompt: str) -> str:
        return await self.provider.generate(user_id, prompt)
