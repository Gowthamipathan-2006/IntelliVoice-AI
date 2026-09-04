from google import genai

from backend.config import GEMINI_API_KEY


# Create Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_response(message: str) -> str:
    """
    Send a user message to Gemini and return the AI response.
    """

    # Validate input
    if not message or not message.strip():
        raise ValueError("Message cannot be empty.")

    # Send request to Gemini using the Interactions API
    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=message.strip()
    )

    # Get generated text
    response = interaction.output_text

    if not response:
        raise RuntimeError("The LLM returned an empty response.")

    return response.strip()