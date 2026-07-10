from app.providers.gemini import GeminiProvider


class AIManager:
    def __init__(self):
        self.provider = GeminiProvider()

    async def generate(self, prompt: str) -> str:
        return await self.provider.generate(prompt)
