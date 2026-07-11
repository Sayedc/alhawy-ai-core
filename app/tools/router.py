from app.tools.calculator import CalculatorTool


calculator = CalculatorTool()


class ToolRouter:

    async def run(self, prompt: str):

        text = prompt.lower().strip()

        allowed = "0123456789+-*/().^×÷ "

        if all(c in allowed for c in text):
            return await calculator.run(text)

        return None
