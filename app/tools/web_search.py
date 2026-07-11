from app.tools.calculator import CalculatorTool
from app.tools.web_search import WebSearchTool


class ToolRouter:

    def __init__(self):
        self.tools = [
            CalculatorTool(),
            WebSearchTool(),
        ]

    async def run(self, prompt: str):

        text = prompt.lower().strip()

        # Calculator
        allowed = "0123456789+-*/().^×÷ "

        if all(c in allowed for c in text):
            return await self.tools[0].run(prompt)

        # Web Search
        keywords = [
            "سعر",
            "اخبار",
            "خبر",
            "bitcoin",
            "btc",
            "ذهب",
            "gold",
            "نفط",
            "usd",
            "eur",
            "شركة",
            "apple",
            "tesla",
            "nvidia",
        ]

        if any(k in text for k in keywords):
            return await self.tools[1].run(prompt)

        return None
