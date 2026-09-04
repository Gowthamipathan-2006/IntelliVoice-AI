import os

from dotenv import load_dotenv


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")


if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured. "
        "Please add it to the .env file."
    )


if not GEMINI_MODEL:
    raise RuntimeError(
        "GEMINI_MODEL is not configured. "
        "Please add it to the .env file."
    )