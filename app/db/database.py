import sqlite3

DB_PATH = "survey_responses.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    with open("app/db/tables.sql", "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
