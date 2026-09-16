# ============================================================
# INTELLIVOICE AI - CONVERSATION MEMORY
# ============================================================

MAX_HISTORY = 10

conversation_history = []


# ============================================================
# GET HISTORY
# ============================================================

def get_history():
    """
    Return the current conversation history.
    """

    return conversation_history.copy()


# ============================================================
# ADD MESSAGE
# ============================================================

def add_message(role: str, content: str):
    """
    Add a message to conversation memory.

    role:
        user
        assistant
    """

    if not content:
        return

    conversation_history.append({
        "role": role,
        "content": str(content).strip()
    })

    # Keep only recent messages
    if len(conversation_history) > MAX_HISTORY:
        del conversation_history[:-MAX_HISTORY]


# ============================================================
# SAVE MEMORY
# ============================================================

def save_memory(user_message: str, ai_response: str):
    """
    Save one complete conversation turn.
    """

    add_message(
        "user",
        user_message
    )

    add_message(
        "assistant",
        ai_response
    )


# ============================================================
# CLEAR MEMORY
# ============================================================

def clear_memory():
    """
    Clear current conversation memory.
    """

    conversation_history.clear()


# ============================================================
# FORMAT HISTORY
# ============================================================

def format_history():
    """
    Convert conversation history into text
    that can be sent to the LLM.
    """

    if not conversation_history:
        return ""

    formatted_history = []

    for message in conversation_history:

        role = message.get("role", "")
        content = message.get("content", "")

        if role == "user":

            formatted_history.append(
                f"User: {content}"
            )

        elif role == "assistant":

            formatted_history.append(
                f"Assistant: {content}"
            )

    return "\n".join(formatted_history)