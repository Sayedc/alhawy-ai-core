from app.tools.calculator import CalculatorTool
from app.tools.crypto import CryptoTool

calculator = CalculatorTool()
crypto = CryptoTool()


class ToolRouter:

    async def run(self, prompt: str):

        result = await calculator.run(prompt)

        if result:
            return result

        result = await crypto.run(prompt)

        if result:
            return result

        return None
