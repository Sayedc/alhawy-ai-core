import logging

from app.tools import load_tools

logger = logging.getLogger(__name__)


class ToolRouter:

    def __init__(self):
        self.registry = load_tools()

    async def run(self, query: str):
        tool = self.registry.find_tool(query)

        if tool is None:
            logger.info(f"No tool found for: {query}")
            return None

        logger.info(f"Selected tool: {tool.name}")

        result = await tool.run(query)

        logger.info(f"Tool result: {result}")

        return result


router = ToolRouter()
