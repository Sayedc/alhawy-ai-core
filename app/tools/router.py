from app.tools import load_tools


class ToolRouter:

    def __init__(self):
        self.registry = load_tools()

    async def run(self, query: str):
        tool = self.registry.find_tool(query)

        if tool is None:
            print(f"No tool found for: {query}")
            return None

        print(f"Selected tool: {tool.name}")

        try:
            result = await tool.run(query)
            print(f"Tool result: {result}")
            return result
        except Exception as e:
            print(f"Tool error: {e}")
            return None


router = ToolRouter()
