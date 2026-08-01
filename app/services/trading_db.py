# app/services/trading_db.py
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

class TradingDB:
    def __init__(self, db_path="trading_data.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # جدول الصفقات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL, -- BUY, SELL
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                total REAL NOT NULL,
                date TEXT NOT NULL,
                status TEXT DEFAULT 'OPEN', -- OPEN, CLOSED
                notes TEXT,
                entry_price REAL,
                exit_price REAL,
                profit_loss REAL,
                profit_loss_percent REAL,
                user_id TEXT
            )
        """)
        
        # جدول التوصيات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL, -- BUY, SELL, HOLD
                target_price REAL,
                stop_loss REAL,
                reason TEXT,
                date TEXT NOT NULL,
                status TEXT DEFAULT 'ACTIVE' -- ACTIVE, CLOSED
            )
        """)
        
        # جدول المحفظة
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                symbol TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL,
                avg_price REAL NOT NULL,
                current_price REAL,
                total_invested REAL,
                current_value REAL,
                profit_loss REAL,
                profit_loss_percent REAL,
                last_updated TEXT
            )
        """)
        
        # جدول المستخدمين المتتبعين
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS followers (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                joined_date TEXT,
                notifications_enabled INTEGER DEFAULT 1
            )
        """)
        
        self.conn.commit()
    
    # ===== دوال الصفقات =====
    
    def add_trade(self, symbol: str, action: str, price: float, quantity: int, notes: str = "") -> int:
        """إضافة صفقة جديدة"""
        cursor = self.conn.cursor()
        total = price * quantity
        cursor.execute("""
            INSERT INTO trades (symbol, action, price, quantity, total, date, notes, entry_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (symbol, action, price, quantity, total, datetime.now().isoformat(), notes, price))
        self.conn.commit()
        trade_id = cursor.lastrowid
        
        # تحديث المحفظة
        self._update_portfolio(symbol)
        
        return trade_id
    
    def close_trade(self, trade_id: int, exit_price: float):
        """إغلاق صفقة"""
        cursor = self.conn.cursor()
        
        # جلب بيانات الصفقة
        trade = cursor.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()
        if not trade:
            return False
        
        entry_price = trade['entry_price']
        quantity = trade['quantity']
        action = trade['action']
        
        # حساب الربح/الخسارة
        if action == 'BUY':
            profit_loss = (exit_price - entry_price) * quantity
        else:  # SELL
            profit_loss = (entry_price - exit_price) * quantity
        
        profit_loss_percent = (profit_loss / (entry_price * quantity)) * 100
        
        cursor.execute("""
            UPDATE trades 
            SET exit_price = ?, profit_loss = ?, profit_loss_percent = ?, status = 'CLOSED'
            WHERE id = ?
        """, (exit_price, profit_loss, profit_loss_percent, trade_id))
        self.conn.commit()
        
        # تحديث المحفظة
        self._update_portfolio(trade['symbol'])
        
        return True
    
    def get_active_trades(self) -> List[Dict]:
        """جلب الصفقات المفتوحة"""
        cursor = self.conn.cursor()
        rows = cursor.execute("SELECT * FROM trades WHERE status = 'OPEN' ORDER BY date DESC").fetchall()
        return [dict(row) for row in rows]
    
    def get_all_trades(self, limit: int = 50) -> List[Dict]:
        """جلب كل الصفقات"""
        cursor = self.conn.cursor()
        rows = cursor.execute("SELECT * FROM trades ORDER BY date DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]
    
    # ===== دوال التوصيات =====
    
    def add_recommendation(self, symbol: str, action: str, target_price: float, 
                          stop_loss: float = None, reason: str = "") -> int:
        """إضافة توصية جديدة"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO recommendations (symbol, action, target_price, stop_loss, reason, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (symbol, action, target_price, stop_loss, reason, datetime.now().isoformat()))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_active_recommendations(self) -> List[Dict]:
        """جلب التوصيات النشطة"""
        cursor = self.conn.cursor()
        rows = cursor.execute("""
            SELECT * FROM recommendations 
            WHERE status = 'ACTIVE' 
            ORDER BY date DESC
        """).fetchall()
        return [dict(row) for row in rows]
    
    # ===== دوال المحفظة =====
    
    def _update_portfolio(self, symbol: str):
        """تحديث المحفظة بناءً على الصفقات"""
        cursor = self.conn.cursor()
        
        # حساب الكمية والمتوسط من الصفقات المفتوحة
        trades = cursor.execute("""
            SELECT action, quantity, entry_price 
            FROM trades 
            WHERE symbol = ? AND status = 'OPEN'
        """, (symbol,)).fetchall()
        
        if not trades:
            # حذف السهم من المحفظة
            cursor.execute("DELETE FROM portfolio WHERE symbol = ?", (symbol,))
            self.conn.commit()
            return
        
        # حساب الكمية الصافية
        total_quantity = 0
        total_cost = 0
        
        for trade in trades:
            if trade['action'] == 'BUY':
                total_quantity += trade['quantity']
                total_cost += trade['quantity'] * trade['entry_price']
            else:  # SELL
                total_quantity -= trade['quantity']
                total_cost -= trade['quantity'] * trade['entry_price']
        
        if total_quantity <= 0:
            cursor.execute("DELETE FROM portfolio WHERE symbol = ?", (symbol,))
            self.conn.commit()
            return
        
        avg_price = total_cost / total_quantity
        
        # تحديث المحفظة
        cursor.execute("""
            INSERT OR REPLACE INTO portfolio 
            (symbol, quantity, avg_price, last_updated)
            VALUES (?, ?, ?, ?)
        """, (symbol, total_quantity, avg_price, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_portfolio(self) -> List[Dict]:
        """جلب المحفظة الحالية"""
        cursor = self.conn.cursor()
        rows = cursor.execute("SELECT * FROM portfolio").fetchall()
        return [dict(row) for row in rows]
    
    def get_portfolio_summary(self) -> Dict:
        """ملخص المحفظة"""
        portfolio = self.get_portfolio()
        total_invested = 0
        total_value = 0
        
        for item in portfolio:
            total_invested += item['quantity'] * item['avg_price']
            total_value += item['quantity'] * item.get('current_price', item['avg_price'])
        
        return {
            "total_invested": total_invested,
            "total_value": total_value,
            "profit_loss": total_value - total_invested,
            "profit_loss_percent": ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
        }
    
    # ===== دوال المتابعين =====
    
    def add_follower(self, user_id: str, username: str):
        """إضافة متابع جديد"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO followers (user_id, username, joined_date)
            VALUES (?, ?, ?)
        """, (user_id, username, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_followers(self) -> List[Dict]:
        """جلب قائمة المتابعين"""
        cursor = self.conn.cursor()
        rows = cursor.execute("SELECT * FROM followers").fetchall()
        return [dict(row) for row in rows]
    
    # ===== دوال تنفيذ الأوامر =====
    
    def execute_buy_order(self, symbol: str, quantity: int, price: float, user_id: str = None) -> dict:
        """
        تنفيذ أمر شراء حقيقي
        """
        cursor = self.conn.cursor()
        
        # حساب القيمة الإجمالية
        total = price * quantity
        
        # إضافة الصفقة
        cursor.execute("""
            INSERT INTO trades (symbol, action, price, quantity, total, date, status, entry_price, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (symbol.upper(), 'BUY', price, quantity, total, datetime.now().isoformat(), 'OPEN', price, user_id))
        
        trade_id = cursor.lastrowid
        
        # تحديث المحفظة
        self._update_portfolio(symbol.upper())
        
        self.conn.commit()
        
        return {
            "trade_id": trade_id,
            "symbol": symbol.upper(),
            "action": "BUY",
            "quantity": quantity,
            "price": price,
            "total": total,
            "status": "OPEN"
        }
    
    def execute_sell_order(self, symbol: str, quantity: int, price: float, user_id: str = None) -> dict:
        """
        تنفيذ أمر بيع حقيقي
        """
        cursor = self.conn.cursor()
        
        # التحقق من وجود الكمية في المحفظة
        portfolio = self.get_portfolio()
        for item in portfolio:
            if item['symbol'] == symbol.upper():
                if item['quantity'] < quantity:
                    return {"error": f"الكمية غير كافية. المتوفر: {item['quantity']}"}
                break
        else:
            return {"error": f"لا تملك أسهم {symbol.upper()}"}
        
        # حساب القيمة الإجمالية
        total = price * quantity
        
        # إضافة الصفقة
        cursor.execute("""
            INSERT INTO trades (symbol, action, price, quantity, total, date, status, entry_price, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (symbol.upper(), 'SELL', price, quantity, total, datetime.now().isoformat(), 'OPEN', price, user_id))
        
        trade_id = cursor.lastrowid
        
        # تحديث المحفظة
        self._update_portfolio(symbol.upper())
        
        self.conn.commit()
        
        return {
            "trade_id": trade_id,
            "symbol": symbol.upper(),
            "action": "SELL",
            "quantity": quantity,
            "price": price,
            "total": total,
            "status": "OPEN"
        }
    
    def get_trade_history(self, user_id: str = None, limit: int = 50) -> List[Dict]:
        """
        جلب تاريخ الصفقات لمستخدم معين
        """
        cursor = self.conn.cursor()
        
        if user_id:
            rows = cursor.execute("""
                SELECT * FROM trades 
                WHERE user_id = ? 
                ORDER BY date DESC 
                LIMIT ?
            """, (user_id, limit)).fetchall()
        else:
            rows = cursor.execute("""
                SELECT * FROM trades 
                ORDER BY date DESC 
                LIMIT ?
            """, (limit,)).fetchall()
        
        return [dict(row) for row in rows]
    
    def calculate_pnl(self, user_id: str = None) -> dict:
        """
        حساب الأرباح والخسائر الحقيقية
        """
        trades = self.get_trade_history(user_id)
        
        total_buy = 0
        total_sell = 0
        open_positions = []
        
        for trade in trades:
            if trade['action'] == 'BUY':
                total_buy += trade['total']
                if trade['status'] == 'OPEN':
                    open_positions.append(trade)
            else:
                total_sell += trade['total']
        
        # حساب القيمة الحالية للصفقات المفتوحة
        current_value = 0
        for pos in open_positions:
            # جلب السعر الحالي (يحتاج استدعاء API)
            current_value += pos['quantity'] * pos['price']  # مؤقت
        
        return {
            "total_invested": total_buy,
            "total_realized": total_sell,
            "unrealized_pnl": current_value - total_buy,
            "realized_pnl": total_sell - total_buy,
            "total_pnl": (total_sell + current_value) - total_buy
        }

# إنشاء كائن واحد للاستخدام
trading_db = TradingDB()
