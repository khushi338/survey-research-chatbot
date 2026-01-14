def validate_answer(question, answer):
    """
    Validates the user's answer based on question type.
    Returns (is_valid, cleaned_answer, error_message)
    """

    if answer is None:
        answer = ""

    answer = answer.strip()

    # Required field check
    if question.get("required", False):
        if answer == "":
            return False, None, "This question is required. Please provide an answer."

    q_type = question.get("type")

    # Number validation
    if q_type == "number":
        if not answer.isdigit():
            return False, None, "Please enter a valid number."
        return True, int(answer), ""

    # Choice validation (CASE-INSENSITIVE, FUTURE-PROOF)
    if q_type == "choice":
        options = question.get("options", [])

        normalized_answer = answer.lower()
        option_map = {opt.lower(): opt for opt in options}

        if normalized_answer not in option_map:
            return False, None, f"Please choose one of these options: {options}"

        # Return the standardized option
        return True, option_map[normalized_answer], ""

    # Text validation
    if q_type == "text":
        if len(answer) < 2:
            return False, None, "Please provide a more meaningful response."
        return True, answer, ""

    return True, answer, ""
