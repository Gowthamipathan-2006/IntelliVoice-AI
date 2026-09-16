import os

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GEMINI API
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)


# ============================================================
# NORMAL GEMINI MODEL
# ============================================================

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# ============================================================
# SEARCH GEMINI MODEL
# ============================================================

GEMINI_SEARCH_MODEL = os.getenv(
    "GEMINI_SEARCH_MODEL",
    "gemini-3.6-flash"
)


# ============================================================
# OLLAMA
# ============================================================

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
)


OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)


# ============================================================
# DEBUG
# ============================================================

print("=" * 60)
print("INTELLIVOICE AI CONFIGURATION")
print("=" * 60)

print(
    f"Normal Gemini model : {GEMINI_MODEL}"
)

print(
    f"Search Gemini model : {GEMINI_SEARCH_MODEL}"
)

print(
    f"Ollama model        : {OLLAMA_MODEL}"
)

print(
    f"Ollama host         : {OLLAMA_HOST}"
)

print("=" * 60)