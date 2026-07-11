from app.database.database import conn, cursor

MAX_HISTORY = 10


def add_message(user_id: int, role: str, text: str):
    cursor.execute(
        """
        INSERT INTO messages(user_id, role, text)
        VALUES (?, ?, ?)
        """,
        (user_id, role, text),
    )
    conn.commit()


def get_history(user_id: int):
    cursor.execute(
        """
        SELECT role, text
        FROM messages
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, MAX_HISTORY),
    )

    rows = cursor.fetchall()

    rows.reverse()

    return [
        {
            "role": role,
            "text": text,
        }
        for role, text in rows
    ]


def clear_history(user_id: int):
    cursor.execute(
        "DELETE FROM messages WHERE user_id=?",
        (user_id,),
    )
    conn.commit()
