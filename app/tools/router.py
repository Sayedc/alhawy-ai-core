from app.tools import load_tools


class ToolRouter:

    def __init__(self):
        self.registry = load_tools()

    def route(self, query: str):
        return self.registry.find_tool(query)


router = ToolRouter()
