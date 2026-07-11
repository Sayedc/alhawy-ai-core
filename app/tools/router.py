from app.tools.calculator import CalculatorTool
from app.tools.web_search import WebSearchTool


calculator = CalculatorTool()
web = WebSearchTool()


class ToolRouter:

    async def run(self, prompt: str):

        text = prompt.lower().strip()

        allowed = "0123456789+-*/().^×÷ "

        # حسابي
        if all(c in allowed for c in text):
            return await calculator.run(text)

        # بحث ويب
        keywords = [
            "bitcoin",
            "btc",
            "eth",
            "gold",
            "news",
            "price",
            "stock",
            "forex",
            "usd",
            "eur",
            "ذهب",
            "بيتكوين",
            "سعر",
            "أخبار",
            "الدولار",
        ]

        if any(k in text for k in keywords):
            return await web.run(prompt)

        return None
