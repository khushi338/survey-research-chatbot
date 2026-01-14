from app.db.database import get_db_connection


def save_response(session_id, survey_id, question_id, answer):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO responses (session_id, survey_id, question_id, answer)
        VALUES (?, ?, ?, ?)
        """,
        (session_id, survey_id, question_id, answer),
    )

    conn.commit()
    conn.close()
