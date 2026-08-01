from app.tools.calculator import CalculatorTool
from app.tools.crypto import CryptoTool
from app.tools.forex import ForexTool
from app.tools.gold import GoldTool
from app.tools.news import NewsTool
from app.tools.stocks import StocksTool
from app.tools.trading_tool import TradingTool  # جديد
from app.tools.recommendation_tool import RecommendationTool  # جديد

from app.tools.registry import registry


def load_tools():
    registry.clear()

    registry.register(CalculatorTool())
    registry.register(CryptoTool())
    registry.register(ForexTool())
    registry.register(GoldTool())
    registry.register(NewsTool())
    registry.register(StocksTool())
    
    # أدوات التداول الجديدة
    registry.register(TradingTool())
    registry.register(RecommendationTool())

    return registry
