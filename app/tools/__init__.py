from app.tools.calculator import CalculatorTool
from app.tools.crypto import CryptoTool


def load_tools():
    return [
        CalculatorTool(),
        CryptoTool(),
    ]
