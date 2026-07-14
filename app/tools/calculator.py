import ast

from app.tools.base import Tool


class CalculatorTool(Tool):

    def __init__(self):
        super().__init__(
            name="calculator",
            description="تنفيذ العمليات الحسابية",
            category="Utility",
            version="1.0",
            priority=100,
        )

    @classmethod
    def can_handle(cls, query: str) -> bool:
        allowed = "0123456789+-*/().^×÷% "

        query = query.strip()

        if not query:
            return False

        return all(char in allowed for char in query)

    async def run(self, query: str, **kwargs) -> str:
        expression = (
            query.replace("^", "**")
            .replace("×", "*")
            .replace("÷", "/")
        )

        try:
            tree = ast.parse(expression, mode="eval")

            for node in ast.walk(tree):
                if not isinstance(
                    node,
                    (
                        ast.Expression,
                        ast.BinOp,
                        ast.UnaryOp,
                        ast.Constant,
                        ast.Add,
                        ast.Sub,
                        ast.Mult,
                        ast.Div,
                        ast.Mod,
                        ast.Pow,
                        ast.USub,
                        ast.UAdd,
                        ast.Load,
                    ),
                ):
                    return None

            result = eval(
                compile(tree, "<calculator>", "eval"),
                {"__builtins__": {}},
                {},
            )

            return str(result)

        except Exception:
            return None
