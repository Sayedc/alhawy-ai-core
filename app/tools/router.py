from app.tools.calculator import CalculatorTool
from app.tools.crypto import CryptoTool


class ToolRouter:

    def __init__(self):

        self.tools = [
            CalculatorTool(),
            CryptoTool(),
        ]

    async def run(self, prompt: str):

        for tool in self.tools:

            if tool.can_handle(prompt):

                return await tool.run(prompt)

        return None
