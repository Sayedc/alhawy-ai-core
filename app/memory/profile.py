import sqlite3

DB_NAME = "alhawy.db"


def get_profile(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            name,
            favorite_market,
            capital,
            risk_level,
            summary
        FROM user_profiles
        WHERE user_id=?
        """,
        (user_id,),
    )

    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "name": row[0],
        "favorite_market": row[1],
        "capital": row[2],
        "risk_level": row[3],
        "summary": row[4],
    }


def save_profile(
    user_id: int,
    name=None,
    favorite_market=None,
    capital=None,
    risk_level=None,
    summary=None,
):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO user_profiles(user_id)
        VALUES(?)
        """,
        (user_id,),
    )

    cur.execute(
        """
        UPDATE user_profiles
        SET
            name=?,
            favorite_market=?,
            capital=?,
            risk_level=?,
            summary=?
        WHERE user_id=?
        """,
        (
            name,
            favorite_market,
            capital,
            risk_level,
            summary,
            user_id,
        ),
    )

    conn.commit()
    conn.close()
