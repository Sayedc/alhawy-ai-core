from app.database.database import conn, cursor


def get_profile(user_id: int):
    cursor.execute(
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

    row = cursor.fetchone()

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
    cursor.execute(
        "INSERT OR IGNORE INTO user_profiles(user_id) VALUES(?)",
        (user_id,),
    )

    cursor.execute(
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
