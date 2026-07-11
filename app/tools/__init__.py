from app.tools.calculator import CalculatorTool
from app.tools.crypto import CryptoTool
from app.tools.forex import ForexTool


def load_tools():
    return [
        CalculatorTool(),
        CryptoTool(),
        ForexTool(),
    ]
