import sqlite3

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

# جدول الرسائل
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# جدول الملفات الشخصية للمستخدمين
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    favorite_market TEXT,
    capital TEXT,
    risk_level TEXT,
    summary TEXT
)
""")

conn.commit()
