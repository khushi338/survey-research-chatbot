def is_question_allowed(question, responses):
    """
    Checks whether a question should be shown
    based on skip logic (show_if condition).
    """
    if "show_if" not in question:
        return True

    condition = question["show_if"]

    for q_id, expected_value in condition.items():
        if responses.get(q_id) != expected_value:
            return False

    return True


def get_next_question(survey, responses):
    """
    Returns the next question to ask.
    If no question is left, returns None.
    """
    for question in survey["questions"]:
        q_id = question["id"]

        # Skip if already answered
        if q_id in responses:
            continue

        # Skip if skip logic condition fails
        if not is_question_allowed(question, responses):
            continue

        return question

    return None


def is_survey_complete(survey, responses):
    """
    Checks if all required questions
    have been answered.
    """
    for question in survey["questions"]:
        if not is_question_allowed(question, responses):
            continue

        if question.get("required", False):
            if question["id"] not in responses:
                return False

    return True
