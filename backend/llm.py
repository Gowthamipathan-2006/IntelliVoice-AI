# ============================================================
# INTELLIVOICE AI - LLM ENGINE
# Gemini + Ollama Fallback
# + Conversation Memory
# + Live Web Search
# + File Analysis Compatibility
# ============================================================

import os
import time
import requests

from dotenv import load_dotenv
from google import genai

from backend.config import GEMINI_API_KEY

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# MEMORY
# ============================================================

try:

    from backend.memory import (
        get_history,
        save_memory
    )

except Exception as error:

    print(
        "Memory import warning:",
        error
    )

    get_history = None
    save_memory = None


# ============================================================
# WEB SEARCH
# ============================================================

try:

    from tools.web_search import search_web

except Exception as error:

    print(
        "Web search import warning:",
        error
    )

    search_web = None


# ============================================================
# GEMINI CONFIGURATION
# ============================================================
from google.genai import types
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


gemini_client = None


if GEMINI_API_KEY:

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(
                timeout=120000
            )
        )

        print(
            f"Gemini client initialized: {GEMINI_MODEL}"
        )

    except Exception as error:

        print(
            f"Gemini client initialization failed: {error}"
        )

else:

    print(
        "GEMINI_API_KEY is missing."
    )


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://127.0.0.1:11434"
).rstrip("/")


OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
)


OLLAMA_TIMEOUT = int(
    os.getenv(
        "OLLAMA_TIMEOUT",
        "120"
    )
)

USE_OLLAMA_FALLBACK = (
    os.getenv(
        "USE_OLLAMA_FALLBACK",
        "true"
    ).lower()
    == "true"
)
# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are IntelliVoice AI, a friendly intelligent personal AI assistant.

Your job is to:

- Understand the user's question clearly.
- Give simple, accurate and useful answers.
- Use natural conversational language.
- Remember relevant information from the conversation.
- Use previous messages when answering follow-up questions.
- If the user tells you their name, remember it during the conversation.
- Do not repeatedly introduce yourself when the user is already chatting with you.
- Do not give exactly the same response repeatedly when the same message is sent again.
- Keep answers reasonably concise unless the user asks for detail.
- Explain technical topics in beginner-friendly language.
- Never pretend to know current information unless it was provided by a live search or tool.
- Do not mention internal model names unless specifically asked.
- Do not mention Gemini or Ollama when answering normal user questions.
- Be warm, polite and helpful.
"""


# ============================================================
# GET CONVERSATION HISTORY
# ============================================================

def _get_conversation_history():
    """
    Safely get conversation history from memory.py.
    """

    if get_history is None:

        return []

    try:

        history = get_history()

        if not history:

            return []

        return history

    except Exception as error:

        print(
            "Memory read error:",
            error
        )

        return []


# ============================================================
# BUILD GEMINI CONVERSATION PROMPT
# ============================================================

def build_prompt(message: str) -> str:
    """
    Build a prompt containing previous conversation
    and the current user message.
    """

    history = _get_conversation_history()


    formatted_history = []


    for item in history:

        if not isinstance(
            item,
            dict
        ):

            continue


        role = item.get(
            "role",
            ""
        )


        content = item.get(
            "content",
            ""
        )


        if not content:

            continue


        if role == "user":

            formatted_history.append(
                f"User: {content}"
            )


        elif role == "assistant":

            formatted_history.append(
                f"Assistant: {content}"
            )


    history_text = "\n".join(
        formatted_history
    )


    # ========================================================
    # FIRST MESSAGE
    # ========================================================

    if not history_text:

        return (
            SYSTEM_INSTRUCTION
            + "\n\n"
            + "Current user message:\n"
            + message.strip()
        )


    # ========================================================
    # MESSAGE WITH HISTORY
    # ========================================================

    return (
        SYSTEM_INSTRUCTION
        + "\n\n"
        + "Previous conversation:\n"
        + history_text
        + "\n\n"
        + "Current user message:\n"
        + message.strip()
        + "\n\n"
        + "Answer the current user message naturally. "
          "Use the previous conversation when relevant. "
          "Do not unnecessarily repeat previous answers."
    )


# ============================================================
# SAVE MEMORY SAFELY
# ============================================================

def _save_memory_safely(
    user_message,
    ai_response
):
    """
    Save the current conversation turn safely.
    Memory errors must never crash the application.
    """

    if save_memory is None:

        print(
            "Memory save skipped: save_memory unavailable."
        )

        return


    try:

        save_memory(
            user_message,
            ai_response
        )

        print(
            "Conversation memory updated."
        )

    except Exception as error:

        print(
            "Memory save error:",
            error
        )


# ============================================================
# GEMINI ERROR TEXT
# ============================================================

def _get_error_text(error):

    try:

        return str(
            error
        ).lower()

    except Exception:

        return ""


# ============================================================
# CHECK WHETHER GEMINI SHOULD FALL BACK
# ============================================================

def _should_fallback_to_ollama(error):

    text = _get_error_text(
        error
    )


    fallback_keywords = [

        # Rate limit / quota
        "429",
        "resource_exhausted",
        "quota_exceeded",
        "rate_limit_exceeded",
        "too_many_requests",

        # Server errors
        "500",
        "internal",
        "api_error",

        "502",
        "bad gateway",

        "503",
        "service_unavailable",
        "unavailable",

        "504",
        "deadline_exceeded",

        # Network
        "timeout",
        "timed out",
        "connection",
        "network",

        # Model/API availability
        "not_found",
        "model_not_found",

        # Overloaded
        "overloaded"
    ]


    return any(
        keyword in text
        for keyword in fallback_keywords
    )


# ============================================================
# GEMINI RESPONSE
# ============================================================

def _generate_with_gemini(
    message,
    max_attempts=2
):
    """
    Generate response using Gemini.
    """

    if gemini_client is None:

        raise RuntimeError(
            "Gemini client is unavailable."
        )


    prompt = build_prompt(
        message
    )


    last_error = None


    for attempt in range(
        1,
        max_attempts + 1
    ):

        try:

            print(
                f"Gemini attempt {attempt}..."
            )


            response = (
                gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt
                )
            )


            # =================================================
            # NORMAL GEMINI TEXT RESPONSE
            # =================================================

            text = getattr(
                response,
                "text",
                None
            )


            if text:

                return text.strip()


            # =================================================
            # FALLBACK RESPONSE EXTRACTION
            # =================================================

            if hasattr(
                response,
                "candidates"
            ):

                try:

                    candidate = (
                        response.candidates[0]
                    )


                    parts = (
                        candidate.content.parts
                    )


                    combined = " ".join(

                        part.text

                        for part in parts

                        if getattr(
                            part,
                            "text",
                            None
                        )

                    )


                    if combined.strip():

                        return combined.strip()


                except Exception:

                    pass


            raise RuntimeError(
                "Gemini returned an empty response."
            )


        except Exception as error:

            last_error = error


            print(
                f"Gemini attempt {attempt} failed:"
            )


            print(
                error
            )


            # -----------------------------------------------
            # If this is not a fallback-type error,
            # immediately raise it.
            # -----------------------------------------------

            if not _should_fallback_to_ollama(
                error
            ):

                raise


            # -----------------------------------------------
            # Retry Gemini once
            # -----------------------------------------------

            if attempt < max_attempts:

                time.sleep(
                    1.5 * attempt
                )


    raise last_error


# ============================================================
# OLLAMA RESPONSE
# ============================================================

def _generate_with_ollama(
    message
):
    """
    Generate response using Ollama.
    Conversation history is included.
    """

    url = (
        f"{OLLAMA_HOST}/api/chat"
    )


    # ========================================================
    # BUILD OLLAMA MESSAGES
    # ========================================================

    messages = [

        {
            "role": "system",
            "content": SYSTEM_INSTRUCTION
        }

    ]


    history = _get_conversation_history()


    for item in history:

        if not isinstance(
            item,
            dict
        ):

            continue


        role = item.get(
            "role"
        )


        content = item.get(
            "content"
        )


        if role in [
            "user",
            "assistant"
        ] and content:

            messages.append({

                "role": role,

                "content": str(
                    content
                )

            })


    # ========================================================
    # CURRENT USER MESSAGE
    # ========================================================

    messages.append({

        "role": "user",

        "content": message.strip()

    })


    # ========================================================
    # OLLAMA PAYLOAD
    # ========================================================

    payload = {

        "model": OLLAMA_MODEL,

        "messages": messages,

        "stream": False,

        "options": {

            "temperature": 0.7,

            "num_predict": 500

        }

    }


    try:

        print(
            "Trying Ollama..."
        )


        response = requests.post(

            url,

            json=payload,

            timeout=OLLAMA_TIMEOUT

        )


        response.raise_for_status()


        data = response.json()


        # ====================================================
        # /api/chat RESPONSE
        # ====================================================

        message_data = data.get(
            "message",
            {}
        )


        answer = message_data.get(
            "content",
            ""
        )


        # ====================================================
        # COMPATIBILITY WITH /api/generate
        # ====================================================

        if not answer:

            answer = data.get(
                "response",
                ""
            )


        answer = str(
            answer
        ).strip()


        if not answer:

            raise RuntimeError(
                "Ollama returned an empty response."
            )


        print(
            "Ollama response generated."
        )


        return answer


    except requests.exceptions.ConnectionError:

        raise RuntimeError(

            "Ollama is not running. "
            "Please start Ollama and make sure "
            f"the model '{OLLAMA_MODEL}' is installed."

        )


    except requests.exceptions.Timeout:

        raise RuntimeError(
            "Ollama took too long to respond."
        )


    except requests.exceptions.HTTPError as error:

        try:

            detail = response.text

        except Exception:

            detail = str(
                error
            )


        raise RuntimeError(
            f"Ollama HTTP error: {detail}"
        )


    except Exception as error:

        raise RuntimeError(
            f"Ollama error: {error}"
        )


# ============================================================
# OLLAMA RESPONSE - COMPATIBILITY FUNCTION
# ============================================================

def generate_ollama_response(
    message: str
):
    """
    Compatibility function used by file_analysis.py.

    This keeps the existing PDF/file-analysis code working
    while using the current Ollama implementation.
    """

    return _generate_with_ollama(
        message
    )


# ============================================================
# MAIN RESPONSE FUNCTION
# ============================================================

def generate_response(
    user_message
):
    """
    Main AI response function.

    Flow:

    1. Try Gemini.
    2. If Gemini fails, use Ollama.
    3. Save successful conversation to memory.
    """

    message = (
        user_message or ""
    ).strip()


    if not message:

        return (
            "Please enter a message and "
            "I will be happy to help you."
        )


    # ========================================================
    # GEMINI
    # ========================================================

    try:

        print(
            "Trying Gemini..."
        )


        answer = _generate_with_gemini(
            message
        )


        print(
            "Gemini response generated."
        )


        # Save successful conversation
        _save_memory_safely(
            message,
            answer
        )


        return answer


    except Exception as gemini_error:

        print(
            "Gemini unavailable."
        )

        print(
            f"Gemini error: {gemini_error}"
        )

        if not USE_OLLAMA_FALLBACK:

            return (
                "I'm sorry, but the AI service is "
                "temporarily unavailable. Please try again."
            )

        print(
            "Switching to Ollama..."
        )


    # ========================================================
    # OLLAMA FALLBACK
    # ========================================================

    try:

        answer = _generate_with_ollama(
            message
        )


        print(
            "Ollama response generated."
        )


        # Save successful conversation
        _save_memory_safely(
            message,
            answer
        )


        return answer


    except Exception as ollama_error:

        print(
            "Ollama fallback failed:"
        )


        print(
            ollama_error
        )


        return (
            "I'm sorry, but I couldn't generate "
            "a response right now. Please try again."
        )


# ============================================================
# LIVE WEB SEARCH RESPONSE
# ============================================================

# ============================================================
# LIVE WEB SEARCH RESPONSE
# ============================================================

def generate_search_response(
    user_message
):
    """
    Perform live web search and convert the results
    into a natural AI response.

    Search flow:

    User question
        ↓
    Live web search
        ↓
    Search results
        ↓
    Gemini summarizes the results
        ↓
    Ollama fallback if Gemini fails
        ↓
    Natural answer for the user
    """

    message = (
        user_message or ""
    ).strip()

    # --------------------------------------------------------
    # Empty query
    # --------------------------------------------------------

    if not message:

        return (
            "Please enter a search query."
        )

    # --------------------------------------------------------
    # Check search availability
    # --------------------------------------------------------

    if search_web is None:

        return (
            "Live web search is currently "
            "unavailable."
        )

    try:

        print("=" * 60)
        print("LIVE SEARCH + AI SUMMARY")
        print("=" * 60)

        # ----------------------------------------------------
        # STEP 1: Get live search results
        # ----------------------------------------------------

        print(
            f"Search query: {message}"
        )

        search_result = search_web(
            message
        )

        search_result = str(
            search_result
        ).strip()

        # ----------------------------------------------------
        # No useful results
        # ----------------------------------------------------

        if not search_result:

            return (
                "I couldn't find useful live "
                "information for that question right now."
            )

        print(
            "Live search completed."
        )

        # ----------------------------------------------------
        # STEP 2: Create summarization prompt
        # ----------------------------------------------------

        summary_prompt = f"""
You are IntelliVoice AI.

The user asked:

"{message}"

Below are LIVE WEB SEARCH RESULTS retrieved just now:

---------------- SEARCH RESULTS ----------------

{search_result}

---------------- END SEARCH RESULTS ------------

Your task is to answer the user's question using
ONLY the information contained in the search results.

IMPORTANT RULES:

1. Give the user a natural conversational answer.
2. Do NOT display raw search result labels such as:
   NEWS 1
   NEWS 2
   Headline
   Source
   Details
   URL
3. Do NOT simply copy the search results.
4. Summarize the most important information.
5. For a news question, mention the main recent news
   items in a short news briefing.
6. Mention the source name when it is available.
7. If a date is available, mention it naturally.
8. Do not invent facts that are not present in the results.
9. Do not claim something is confirmed if the search
   results do not establish that.
10. Keep the answer concise and suitable for voice output.
11. Use simple English.
12. Do not include URLs unless the user specifically
    asks for links.
13. Start directly with the answer.
14. If there are multiple important news stories,
    organize them naturally with short bullet points.
15. If the results are weak or unrelated, clearly say
    that the available search results are limited.

For a question such as:

"Tell me the live news in Vijayawada"

respond like a short live news briefing, for example:

"Here are the latest Vijayawada updates. Police in
Krishnalanka have reportedly seized gelatin sticks and
electronic detonators, and an investigation is underway.
There is also a recent weather update showing overcast
conditions in Vijayawada."

Do not use this example as factual information.
Use the actual search results above.
"""

        # ====================================================
        # STEP 3: Try Gemini
        # ====================================================

        if gemini_client is not None:

            try:

                print(
                    "Sending live search results to Gemini..."
                )

                response = (
                    gemini_client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=summary_prompt
                    )
                )

                answer = getattr(
                    response,
                    "text",
                    None
                )

                if answer:

                    answer = answer.strip()

                    if answer:

                        print(
                            "Gemini live-news summary generated."
                        )

                        return answer

            except Exception as error:

                print(
                    "Gemini search-summary failed:"
                )

                print(
                    error
                )

                print(
                    "Trying Ollama for search summary..."
                )

        # ====================================================
        # STEP 4: Ollama fallback
        # ====================================================

        ollama_prompt = summary_prompt

        try:

            answer = _generate_with_ollama(
                ollama_prompt
            )

            answer = str(
                answer
            ).strip()

            if answer:

                print(
                    "Ollama live-news summary generated."
                )

                return answer

        except Exception as error:

            print(
                "Ollama search-summary failed:"
            )

            print(
                error
            )

        # ====================================================
        # STEP 5: Last-resort result
        # ====================================================

        print(
            "AI summarization unavailable."
        )

        return (
            "I found live search results, but "
            "I couldn't summarize them right now. "
            "Please try again."
        )

    except Exception as error:

        print(
            "=" * 60
        )

        print(
            "LIVE SEARCH ERROR:"
        )

        print(
            repr(error)
        )

        print(
            "=" * 60
        )

        return (
            "Sorry, I couldn't access and summarize "
            "live web information right now."
        )
    """
    Generate a live web search result.
    """

    message = (
        user_message or ""
    ).strip()


    if not message:

        return (
            "Please enter a search query."
        )


    if search_web is None:

        return (
            "Live web search is currently "
            "unavailable."
        )


    try:

        print(
            "Running live web search..."
        )


        result = search_web(
            message
        )


        return str(
            result
        )


    except Exception as error:

        print(
            "Web search error:",
            error
        )


        return (
            "Sorry, I couldn't access "
            "live web information right now."
        )