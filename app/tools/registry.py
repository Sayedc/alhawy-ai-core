from typing import Dict, List, Optional

from .base import Tool


class ToolRegistry:
    """
    Registry مسؤول عن تسجيل وإدارة جميع الأدوات (Tools).
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        تسجيل أداة جديدة.
        """
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        """
        حذف أداة من الـ Registry.
        """
        self._tools.pop(name, None)

    def get(self, name: str) -> Optional[Tool]:
        """
        الحصول على أداة بالاسم.
        """
        return self._tools.get(name)

    def all(self) -> List[Tool]:
        """
        إرجاع جميع الأدوات.
        """
        return list(self._tools.values())

    def enabled_tools(self) -> List[Tool]:
        """
        إرجاع الأدوات المفعلة فقط.
        """
        return [
            tool
            for tool in self._tools.values()
            if tool.is_available()
        ]

    def find_tool(self, query: str) -> Optional[Tool]:
        """
        البحث عن أفضل أداة لمعالجة الرسالة.
        """
        
        print(f"Query: {query}")

        for tool in self.enabled_tools():
            try:
                result = tool.can_handle(query)
                print(f"{tool.name}: {result}")
            except Exception as e:
                print(f"{tool.name}: ERROR {e}")

        candidates = [
            tool
            for tool in self.enabled_tools()
            if tool.can_handle(query)
        ]

        if not candidates:
            print("No candidates")
            return None

        candidates.sort(key=lambda t: t.priority)

        print("Selected:", candidates[0].name)

        return candidates[0]

    def clear(self) -> None:
        """
        حذف جميع الأدوات.
        """
        self._tools.clear()

    def count(self) -> int:
        """
        عدد الأدوات المسجلة.
        """
        return len(self._tools)


registry = ToolRegistry()
