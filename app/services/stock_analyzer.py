# app/services/stock_analyzer.py
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class StockAnalyzer:
    """
    تحليل متقدم للأسهم باستخدام Yahoo Finance و TA-Lib
    """
    
    def __init__(self):
        self.symbols = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corp",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com",
            "TSLA": "Tesla Inc.",
            "META": "Meta Platforms",
            "NVDA": "NVIDIA Corp",
            "JPM": "JPMorgan Chase",
            "VTI": "Vanguard Total Stock Market",
            "SPY": "SPDR S&P 500 ETF",
        }
    
    async def get_top_stocks(self) -> List[Dict]:
        """
        جلب أفضل الأسهم بناءً على عدة مؤشرات
        """
        results = []
        
        for symbol, name in self.symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # جلب البيانات التاريخية
                hist = ticker.history(period="1mo")
                
                if hist.empty:
                    continue
                
                # حساب المؤشرات
                current_price = info.get('regularMarketPrice', 0)
                prev_close = info.get('previousClose', current_price)
                
                # التغير اليومي
                daily_change = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
                
                # متوسط الحجم
                avg_volume = hist['Volume'].mean()
                current_volume = hist['Volume'].iloc[-1]
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                
                # RSI (مؤشر القوة النسبية)
                rsi = self._calculate_rsi(hist['Close'])
                
                # المتوسطات المتحركة
                ma_50 = hist['Close'].rolling(50).mean().iloc[-1]
                ma_200 = hist['Close'].rolling(200).mean().iloc[-1]
                
                # قوة السهم
                score = 0
                
                # 1. اتجاه السعر
                if daily_change > 2:
                    score += 1
                elif daily_change > 0:
                    score += 0.5
                
                # 2. RSI
                if rsi < 30:  # منطقة ذهبية (oversold)
                    score += 1.5
                elif rsi < 50:
                    score += 0.5
                elif rsi > 70:  # منطقة خطر (overbought)
                    score -= 1
                
                # 3. الحجم
                if volume_ratio > 2:
                    score += 1  # حجم مرتفع = اهتمام
                elif volume_ratio > 1:
                    score += 0.5
                
                # 4. المتوسطات المتحركة
                if current_price > ma_50:
                    score += 0.5
                if current_price > ma_200:
                    score += 0.5
                
                # 5. التوصيات
                recommendation = info.get('recommendationKey', 'none')
                if recommendation == 'buy':
                    score += 1
                elif recommendation == 'strong_buy':
                    score += 1.5
                
                # 6. السعر المستهدف
                target = info.get('targetMeanPrice', current_price)
                if target > current_price * 1.1:
                    score += 1
                elif target > current_price * 1.05:
                    score += 0.5
                
                results.append({
                    "symbol": symbol,
                    "name": name,
                    "price": current_price,
                    "change": daily_change,
                    "rsi": rsi,
                    "volume_ratio": volume_ratio,
                    "score": score,
                    "recommendation": recommendation,
                    "target_price": target,
                    "ma_50": ma_50,
                    "ma_200": ma_200,
                    "market_cap": info.get('marketCap', 0),
                    "pe_ratio": info.get('trailingPE', 0),
                })
                
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue
        
        # ترتيب حسب النتيجة
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def _calculate_rsi(self, prices, period=14):
        """حساب مؤشر RSI"""
        if len(prices) < period:
            return 50
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    
    async def get_stock_news(self, symbol: str) -> List[Dict]:
        """
        جلب أخبار سهم معين
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                return []
            
            # ترشيح الأخبار المهمة
            important_news = []
            for item in news[:5]:
                important_news.append({
                    "title": item.get('title', ''),
                    "link": item.get('link', ''),
                    "publisher": item.get('publisher', ''),
                    "date": datetime.fromtimestamp(item.get('providerPublishTime', 0)).isoformat(),
                    "sentiment": self._analyze_sentiment(item.get('title', ''))
                })
            
            return important_news
            
        except Exception:
            return []
    
    def _analyze_sentiment(self, text: str) -> str:
        """تحليل المشاعر للأخبار"""
        positive = ["up", "high", "growth", "profit", "positive", "rise", "surge", "beat", "record"]
        negative = ["down", "low", "loss", "negative", "fall", "drop", "miss", "decline", "crash"]
        
        text_lower = text.lower()
        pos_score = sum(1 for word in positive if word in text_lower)
        neg_score = sum(1 for word in negative if word in text_lower)
        
        if pos_score > neg_score:
            return "إيجابي"
        elif neg_score > pos_score:
            return "سلبي"
        else:
            return "محايد"

stock_analyzer = StockAnalyzer()
