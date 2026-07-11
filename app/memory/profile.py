import sqlite3

DB_NAME = "alhawy.db"


def get_profile(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT name,favorite_market,capital,risk_level,summary FROM user_profiles WHERE user_id=?",
        (user_id,),
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "name": row[0],
        "favorite_market": row[1],
        "capital": row[2],
        "risk_level": row[3],
        "summary": row[4],
    }


def save_profile(user_id: int, **kwargs):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO user_profiles(user_id)
        VALUES(?)
        """,
        (user_id,),
    )

    for key, value in kwargs.items():
        cur.execute(
            f"UPDATE user_profiles SET {key}=? WHERE user_id=?",
            (value, user_id),
        )

    conn.commit()
    conn.close()
