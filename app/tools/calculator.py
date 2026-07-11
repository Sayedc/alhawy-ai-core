herefrom app.tools.base import Tool


class CalculatorTool(Tool):

    name = "calculator"

    description = "تنفيذ العمليات الحسابية"

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
