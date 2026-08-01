from app.tools import load_tools


class ToolRouter:

    def __init__(self):
        self.registry = load_tools()

    async def run(self, query: str):
        tool = self.registry.find_tool(query)

        if tool is None:
            return None

        return await tool.run(query)


router = ToolRouter()
