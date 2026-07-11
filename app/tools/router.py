from app.tools import load_tools


class ToolRouter:

    def __init__(self):
        self.tools = load_tools()

    async def run(self, prompt: str):

        for tool in self.tools:

            if tool.can_handle(prompt):
                return await tool.run(prompt)

        return None
