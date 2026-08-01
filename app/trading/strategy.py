import random
from typing import List, Dict
from app.services.market_service import market_service


class StrategyManager:
    """إدارة استراتيجيات التداول"""

    STRATEGIES = {
        "rsi": "استراتيجية RSI",
        "macd": "استراتيجية MACD", 
        "bollinger": "استراتيجية بولينجر باند",
        "trend": "استراتيجية الاتجاه",
        "breakout": "استراتيجية الاختراق"
    }

    def __init__(self, strategy_name: str = "trend"):
        self.strategy_name = strategy_name

    async def analyze_all_markets(self) -> List[Dict]:
        """تحليل كل الأسواق حسب الاستراتيجية"""
        signals = []

        # تحليل العملات الرقمية
        crypto_signals = await self._analyze_crypto()
        signals.extend(crypto_signals)

        # تحليل الذهب
        gold_signal = await self._analyze_gold()
        if gold_signal:
            signals.append(gold_signal)

        # تحليل الفوركس
        forex_signals = await self._analyze_forex()
        signals.extend(forex_signals)

        # تحليل الأسهم
        stock_signals = await self._analyze_stocks()
        signals.extend(stock_signals)

        return signals

    async def _analyze_crypto(self) -> List[Dict]:
        """تحليل العملات الرقمية"""
        signals = []
        symbols = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA"]

        for symbol in symbols:
            data = await market_service.get_crypto_price(symbol.lower())
            if not data:
                continue

            # تحليل باستخدام الاستراتيجية المختارة
            signal = await self._apply_strategy(symbol, data, "crypto")
            if signal:
                signals.append(signal)

        return signals

    async def _analyze_gold(self) -> Dict:
        """تحليل الذهب"""
        data = await market_service.get_gold_price()
        if not data:
            return None

        return await self._apply_strategy("XAU", data, "commodity")

    async def _analyze_forex(self) -> List[Dict]:
        """تحليل الفوركس"""
        signals = []
        pairs = ["EUR/USD", "GBP/USD", "USD/JPY"]

        for pair in pairs:
            base, target = pair.split('/')
            data = await market_service.get_forex_rate(base, target)
            if not data:
                continue

            signal = await self._apply_strategy(pair, data, "forex")
            if signal:
                signals.append(signal)

        return signals

    async def _analyze_stocks(self) -> List[Dict]:
        """تحليل الأسهم"""
        signals = []
        stocks = ["AAPL", "TSLA", "NVDA", "AMZN", "META"]

        for stock in stocks:
            data = await market_service.get_stock_price(stock)
            if not data:
                continue

            signal = await self._apply_strategy(stock, data, "stock")
            if signal:
                signals.append(signal)

        return signals

    async def _apply_strategy(self, symbol: str, data: Dict, market_type: str) -> Dict:
        """تطبيق الاستراتيجية"""
        # هنا هنطبق الاستراتيجية الفعلية
        # حالياً مجرد محاكاة
        confidence = random.randint(60, 95)
        price = data.get('price', 0)

        if confidence > 70:
            return {
                "market": market_type,
                "symbol": symbol,
                "action": "BUY" if random.random() > 0.5 else "SELL",
                "price": price,
                "target": price * (1 + random.randint(1, 5) / 100),
                "stop_loss": price * (1 - random.randint(1, 3) / 100),
                "profit_percent": random.randint(1, 5),
                "loss_percent": random.randint(1, 3),
                "confidence": confidence,
                "reason": f"تحليل إيجابي لـ {symbol} باستخدام استراتيجية {self.strategy_name}",
                "strategy": self.strategy_name
            }
        return None

    def set_strategy(self, strategy_name: str):
        """تغيير الاستراتيجية"""
        if strategy_name in self.STRATEGIES:
            self.strategy_name = strategy_name
            return True
        return False

    def get_strategies(self) -> Dict:
        """جلب قائمة الاستراتيجيات"""
        return self.STRATEGIES
