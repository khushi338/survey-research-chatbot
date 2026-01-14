import sqlite3
import pandas as pd
import os

# Path to SQLite database
DB_PATH = "survey_responses.db"


def export_responses_to_csv(
    output_path="data/processed/survey_results.csv"
):
    """
    Export all survey responses from SQLite DB to a CSV file.
    Automatically creates the output directory if it does not exist.
    """

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        session_id,
        survey_id,
        question_id,
        answer,
        created_at
    FROM responses
    ORDER BY created_at
    """

    # Load data into DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Export to CSV
    df.to_csv(output_path, index=False)

    return output_path


def get_question_response_counts():
    """
    Returns count of responses per question and answer.
    Useful for frequency analysis.
    """
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        question_id,
        answer,
        COUNT(*) AS response_count
    FROM responses
    GROUP BY question_id, answer
    ORDER BY question_id, response_count DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def get_completion_stats():
    """
    Returns number of answered questions per session.
    Useful for completion and drop-off analysis.
    """
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        session_id,
        COUNT(DISTINCT question_id) AS answered_questions
    FROM responses
    GROUP BY session_id
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df
