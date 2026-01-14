from app.db.analytics import (
    get_question_response_counts,
    get_completion_stats
)

import json
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.core.survey_engine import get_next_question, is_survey_complete
from app.core.validation import validate_answer
from app.db.database import init_db
from app.db.crud import save_response

app = FastAPI(title="Survey Research Assistant API")

# Load survey once
with open("surveys/job_satisfaction.json", "r", encoding="utf-8") as f:
    SURVEY = json.load(f)


# ---------- Request Models ----------
class AnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str


# ---------- In-memory session storage ----------
SESSIONS = {}  # session_id -> responses dict


@app.on_event("startup")
def startup_event():
    init_db()


# ---------- API Endpoints ----------

@app.post("/start-survey")
def start_survey():
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {}
    return {
        "session_id": session_id,
        "survey_id": SURVEY["survey_id"],
        "message": "Survey started successfully"
    }


@app.get("/next-question/{session_id}")
def next_question(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Invalid session ID")

    responses = SESSIONS[session_id]
    next_q = get_next_question(SURVEY, responses)

    if not next_q:
        return {
            "completed": True,
            "message": "Survey completed"
        }

    return {
        "completed": False,
        "question": {
            "id": next_q["id"],
            "text": next_q["text"],
            "type": next_q["type"],
            "options": next_q.get("options")
        }
    }


@app.post("/submit-answer")
def submit_answer(payload: AnswerRequest):
    session_id = payload.session_id

    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Invalid session ID")

    responses = SESSIONS[session_id]

    # Find question
    question = next(
        (q for q in SURVEY["questions"] if q["id"] == payload.question_id),
        None
    )

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Validate answer
    is_valid, cleaned_answer, error_msg = validate_answer(question, payload.answer)

    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Save response
    responses[payload.question_id] = cleaned_answer

    save_response(
        session_id=session_id,
        survey_id=SURVEY["survey_id"],
        question_id=payload.question_id,
        answer=str(cleaned_answer),
    )

    # Check completion
    completed = is_survey_complete(SURVEY, responses)

    return {
        "message": "Answer recorded",
        "completed": completed
    }

@app.get("/analytics/response-counts")
def response_counts():
    df = get_question_response_counts()
    return df.to_dict(orient="records")


@app.get("/analytics/completion-stats")
def completion_stats():
    df = get_completion_stats()
    return df.to_dict(orient="records")

