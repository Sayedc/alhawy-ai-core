from app.tools.base import Tool


class CalculatorTool(Tool):

    name = "calculator"

    description = "تنفيذ العمليات الحسابية"

    def can_handle(self, query: str) -> bool:

        allowed = "0123456789+-*/().^×÷ "

        return all(c in allowed for c in query.strip())

    async def run(self, query: str):

        expression = (
            query.replace("^", "**")
            .replace("×", "*")
            .replace("÷", "/")
        )

        try:
            result = eval(expression, {"__builtins__": {}})

            return str(result)

        except Exception:
            return None
