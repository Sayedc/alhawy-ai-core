from app.tools.calculator import CalculatorTool
from app.tools.crypto import CryptoTool
from app.tools.forex import ForexTool
from app.tools.gold import GoldTool
from app.tools.news import NewsTool
from app.tools.stocks import StocksTool

from app.tools.registry import registry


def load_tools():
    registry.clear()

    registry.register(CalculatorTool())
    registry.register(CryptoTool())
    registry.register(ForexTool())
    registry.register(GoldTool())
    registry.register(NewsTool())
    registry.register(StocksTool())

    return registry
