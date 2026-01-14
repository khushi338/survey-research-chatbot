import streamlit as st
import requests
import pandas as pd

from app.db.analytics import (
    get_question_response_counts,
    get_completion_stats
)

# ---------------- Configuration ----------------
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Survey Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 Survey Research Assistant")

tab1, tab2 = st.tabs(["🗨️ Chatbot", "📊 Analytics"])

# ---------------- Session State ----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "completed" not in st.session_state:
    st.session_state.completed = False


# ---------------- Helper Functions ----------------
def start_survey():
    response = requests.post(f"{API_BASE_URL}/start-survey")
    data = response.json()
    st.session_state.session_id = data["session_id"]
    st.session_state.completed = False
    fetch_next_question()


def fetch_next_question():
    response = requests.get(
        f"{API_BASE_URL}/next-question/{st.session_state.session_id}"
    )
    data = response.json()

    if data.get("completed"):
        st.session_state.completed = True
        st.session_state.current_question = None
    else:
        st.session_state.current_question = data["question"]


def submit_answer(answer):
    payload = {
        "session_id": st.session_state.session_id,
        "question_id": st.session_state.current_question["id"],
        "answer": answer,
    }

    response = requests.post(
        f"{API_BASE_URL}/submit-answer", json=payload
    )

    if response.status_code == 200:
        fetch_next_question()
    else:
        st.error(response.json().get("detail", "Error submitting answer"))


# =================================================
# 🗨️ TAB 1: CHATBOT
# =================================================
with tab1:
    st.subheader("🗨️ Conversational Survey")

    if st.session_state.session_id is None:
        st.button("Start Survey", on_click=start_survey)

    elif st.session_state.completed:
        st.success("🎉 Survey completed successfully!")
        st.write("Thank you for your participation.")

    else:
        q = st.session_state.current_question

        if q:
            st.write(f"**BOT:** {q['text']}")

            # Choice question
            if q["type"] == "choice":
                answer = st.selectbox(
                    "Select an option",
                    q["options"],
                    key=q["id"]
                )

            # Number question
            elif q["type"] == "number":
                answer = st.text_input(
                    "Enter a number",
                    key=q["id"]
                )

            # Text question
            else:
                answer = st.text_input(
                    "Your answer",
                    key=q["id"]
                )

            if st.button("Send"):
                submit_answer(answer)


# =================================================
# 📊 TAB 2: ANALYTICS DASHBOARD
# =================================================
with tab2:
    st.subheader("📊 Survey Analytics Dashboard")

    try:
        response_df = get_question_response_counts()
        completion_df = get_completion_stats()

        # ---------------- Response Distribution ----------------
        st.markdown("### 🔢 Response Distribution")
        st.dataframe(response_df, use_container_width=True)

        st.markdown("### 📈 Responses per Question")
        responses_per_q = (
            response_df.groupby("question_id")["response_count"].sum()
        )
        st.bar_chart(responses_per_q)

        # ---------------- Completion Stats ----------------
        st.markdown("### ✅ Survey Completion Stats")
        st.dataframe(completion_df, use_container_width=True)

        st.markdown("### 📉 Questions Answered per Session")
        st.bar_chart(
            completion_df.set_index("session_id")["answered_questions"]
        )

    except Exception as e:
        st.warning("No analytics data available yet.")
        st.text(str(e))
