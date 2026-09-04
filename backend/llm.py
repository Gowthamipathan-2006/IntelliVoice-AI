from google import genai
from google.genai.errors import APIError

from backend.config import GEMINI_API_KEY, GEMINI_MODEL


client = genai.Client(api_key=GEMINI_API_KEY)


def generate_response(message: str) -> str:
    """
    Send a user message to Gemini and return the AI response.
    Handles common API errors gracefully.
    """

    # Validate input
    if not message or not message.strip():
        raise ValueError("Message cannot be empty.")

    try:
        interaction = client.interactions.create(
            model=GEMINI_MODEL,
            input=message.strip(),
        )

        response = interaction.output_text

        if not response:
            return "Sorry, I couldn't generate a response."

        return response.strip()

    except APIError as e:
        # Handle Gemini API errors
        if getattr(e, "code", None) == 429:
            return (
                "⚠️ Gemini API quota has been exceeded. "
                "Please wait and try again later."
            )

        if getattr(e, "code", None) == 401:
            return (
                "⚠️ Gemini API authentication failed. "
                "Please check your API key."
            )

        if getattr(e, "code", None) == 403:
            return (
                "⚠️ Gemini API access was denied. "
                "Please check your API key and project permissions."
            )

        if getattr(e, "code", None) == 404:
            return (
                f"⚠️ The Gemini model '{GEMINI_MODEL}' "
                "is unavailable for this API configuration."
            )

        return (
            "⚠️ Gemini API error occurred. "
            "Please try again later."
        )

    except Exception as e:
        print(f"Unexpected error: {e}")

        return (
            "⚠️ Something went wrong while contacting the AI service. "
            "Please try again later."
        )