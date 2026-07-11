import httpx

from app.tools.base import Tool


class WebSearchTool(Tool):

    name = "web"

    description = "Search the web"

    async def run(self, query: str):

        async with httpx.AsyncClient(timeout=30) as client:

            r = await client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                },
            )

            data = r.json()

            text = data.get("AbstractText")

            if text:
                return text

            related = data.get("RelatedTopics", [])

            if related:

                first = related[0]

                if isinstance(first, dict):
                    return first.get("Text")

            return None
