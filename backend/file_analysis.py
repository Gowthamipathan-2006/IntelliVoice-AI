# ============================================================
# INTELLIVOICE AI - FILE ANALYSIS
# PDF + IMAGE ANALYSIS
# ============================================================

import io
import os
import time
from typing import Optional

from pypdf import PdfReader

from backend.llm import generate_ollama_response

from google import genai
from google.genai import types


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

ALLOWED_PDF_TYPES = {
    "application/pdf"
}

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


# ============================================================
# ACTIVE DOCUMENT CONTEXT
# ============================================================

active_document_context = ""
active_document_name = ""


def get_active_document_context() -> str:
    return active_document_context


def get_active_document_name() -> str:
    return active_document_name


def clear_active_document_context():
    global active_document_context, active_document_name

    active_document_context = ""
    active_document_name = ""


def _set_active_document(
    extracted_text: str,
    filename: str
):
    global active_document_context, active_document_name

    active_document_context = (
        extracted_text or ""
    )[:30000]

    active_document_name = filename or ""


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(
    file_bytes: bytes
) -> str:

    try:

        pdf_file = io.BytesIO(
            file_bytes
        )

        reader = PdfReader(
            pdf_file
        )

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            try:

                text = page.extract_text()

                if text:

                    pages.append(
                        f"Page {page_number}:\n"
                        f"{text.strip()}"
                    )

            except Exception as page_error:

                print(
                    f"PDF page {page_number} "
                    f"extraction error: "
                    f"{repr(page_error)}"
                )

        extracted_text = "\n\n".join(
            pages
        ).strip()

        return extracted_text

    except Exception as e:

        print("=" * 60)
        print("PDF EXTRACTION ERROR")
        print(f"Error: {repr(e)}")
        print("=" * 60)

        raise RuntimeError(
            "Unable to extract text from the PDF."
        )


# ============================================================
# LOCAL PDF SUMMARY
# ============================================================

def create_local_pdf_summary(
    extracted_text: str,
    filename: str
) -> str:

    if not extracted_text:

        return (
            "I could not extract readable text "
            "from this PDF. It may be a scanned "
            "or image-based PDF."
        )

    max_text_length = 30000

    if len(extracted_text) > max_text_length:

        extracted_text = (
            extracted_text[:max_text_length]
            + "\n\n[Document text truncated because "
              "the PDF is very large.]"
        )

    words = extracted_text.split()

    word_count = len(words)

    character_count = len(
        extracted_text
    )

    lines = [
        line.strip()
        for line in extracted_text.splitlines()
        if line.strip()
    ]

    response = f"""
📄 PDF Analysis

Filename: {filename}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Document Information

• Approximate words: {word_count}
• Characters extracted: {character_count}
• Text sections detected: {len(lines)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Extracted Content

{extracted_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Analysis Status

The PDF text was successfully extracted.
"""

    return response.strip()


# ============================================================
# PDF QUESTION ANSWERING
# ============================================================

def answer_pdf_question(
    extracted_text: str,
    question: str,
    filename: str
) -> str:

    max_text_length = 30000

    if len(extracted_text) > max_text_length:

        extracted_text = (
            extracted_text[:max_text_length]
            + "\n\n[Document text truncated because "
              "the PDF is very large.]"
        )

    prompt = f"""
You are IntelliVoice AI, an intelligent document assistant.

You must answer the user's question using ONLY the
information contained in the uploaded PDF.

Do not invent information.

If the answer is not present in the PDF, clearly say:

"The answer is not available in the uploaded PDF."

If the user asks for a summary, provide a concise,
well-structured summary using bullet points.

If the user asks a specific question, answer directly
and explain briefly using information from the document.

Uploaded PDF:
{filename}

============================================================

PDF CONTENT:

{extracted_text}

============================================================

USER QUESTION:

{question}

============================================================

ANSWER:
"""

    try:

        print("=" * 60)
        print("OLLAMA PDF QUESTION ANSWERING")
        print("=" * 60)
        print(f"PDF      : {filename}")
        print(f"Question : {question}")
        print("=" * 60)

        answer = generate_ollama_response(
            prompt
        )

        if answer:

            return f"""
📄 PDF Question Answer

Filename: {filename}

Question:
{question}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 IntelliVoice AI Answer

{answer}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Answer generated using your local Ollama AI model.
""".strip()

        return (
            "I could not generate an answer "
            "from the uploaded PDF."
        )

    except Exception as e:

        print("=" * 60)
        print("OLLAMA PDF ANALYSIS ERROR")
        print("=" * 60)

        print(
            f"Error type: {type(e).__name__}"
        )

        print(
            f"Error     : {repr(e)}"
        )

        print("=" * 60)

        return (
            "I extracted the PDF successfully, "
            "but I could not generate an AI "
            "answer right now.\n\n"
            f"Reason: {str(e)}"
        )


# ============================================================
# PDF ANALYSIS
# ============================================================

def analyze_pdf(
    file_bytes: bytes,
    filename: str,
    question: Optional[str] = None
) -> str:

    extracted_text = extract_pdf_text(
        file_bytes
    )

    if extracted_text:

        _set_active_document(
            extracted_text,
            filename
        )

    if not extracted_text:

        return (
            "I could not extract readable text "
            "from this PDF. It may be a scanned "
            "or image-based PDF."
        )

    if question and question.strip():

        return answer_pdf_question(
            extracted_text=extracted_text,
            question=question.strip(),
            filename=filename
        )

    return create_local_pdf_summary(
        extracted_text,
        filename
    )


# ============================================================
# GEMINI IMAGE UNDERSTANDING
# ============================================================
# ============================================================
# GEMINI IMAGE UNDERSTANDING
# ============================================================

def generate_image_answer(
    file_bytes: bytes,
    mime_type: str,
    question: str
) -> str:
    """
    Send the uploaded image to Gemini for visual understanding.

    The function retries temporary Gemini 503/429 errors.
    """

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "GEMINI_API_KEY was not found "
            "in the environment."
        )

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=120000
        )
    )

    image_part = types.Part.from_bytes(
        data=file_bytes,
        mime_type=mime_type
    )

    prompt = f"""
You are IntelliVoice AI, an intelligent visual assistant.

Analyze the uploaded image carefully.

Answer the user's question based only on what can
actually be seen in the image.

Do not invent objects, text, people, numbers,
or facts that are not visible.

If text appears in the image, read it carefully
when possible.

If the question is general, explain the important
things visible in the image.

Keep the answer clear, natural, simple and concise.

USER QUESTION:

{question}
"""

    # --------------------------------------------------------
    # Models to try
    # --------------------------------------------------------

    primary_model = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash"
    )

    backup_model = os.getenv(
        "GEMINI_IMAGE_MODEL",
        ""
    ).strip()

    models_to_try = [
        primary_model
    ]

    if backup_model and backup_model not in models_to_try:

        models_to_try.append(
            backup_model
        )

    # --------------------------------------------------------
    # Try each model
    # --------------------------------------------------------

    last_error = None

    for model_name in models_to_try:

        for attempt in range(1, 3):

            try:

                print("=" * 60)
                print("GEMINI IMAGE UNDERSTANDING")
                print("=" * 60)
                print("Model:", model_name)
                print("Attempt:", attempt)
                print("MIME TYPE:", mime_type)
                print("IMAGE SIZE:", len(file_bytes), "bytes")
                print("QUESTION:", question)
                print("=" * 60)

                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        image_part,
                        prompt
                    ]
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
                            "Gemini image analysis successful."
                        )

                        return answer

                raise RuntimeError(
                    "Gemini returned an empty image response."
                )

            except Exception as error:

                last_error = error

                error_text = str(
                    error
                ).lower()

                print(
                    f"Gemini image attempt "
                    f"{attempt} failed:"
                )

                print(error)

                # ------------------------------------------------
                # Retry temporary errors
                # ------------------------------------------------

                temporary_error = any(
                    keyword in error_text
                    for keyword in [
                        "503",
                        "unavailable",
                        "high demand",
                        "429",
                        "resource_exhausted",
                        "quota",
                        "rate limit",
                        "timeout",
                        "timed out",
                        "internal server error"
                    ]
                )

                if temporary_error and attempt < 2:

                    print(
                        "Temporary Gemini error."
                    )

                    print(
                        "Retrying in 3 seconds..."
                    )

                    time.sleep(3)

                    continue

                break

    # --------------------------------------------------------
    # All attempts failed
    # --------------------------------------------------------

    if last_error:

        raise RuntimeError(
            f"Gemini image analysis failed: "
            f"{last_error}"
        )

    raise RuntimeError(
        "Gemini image analysis failed."
    )


# ============================================================
# IMAGE ANALYSIS
# ============================================================

def analyze_image(
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    question: Optional[str] = None
) -> str:

    if mime_type not in ALLOWED_IMAGE_TYPES:

        return (
            "Unsupported image format. "
            "Please upload JPG, PNG, or WebP."
        )

    print("=" * 60)
    print("IMAGE ANALYSIS")
    print("=" * 60)
    print("Filename:", filename)
    print("Type:", mime_type)
    print("Size:", len(file_bytes), "bytes")
    print("=" * 60)

    # --------------------------------------------------------
    # Default question
    # --------------------------------------------------------

    if question and question.strip():

        user_question = question.strip()

    else:

        user_question = (
            "Describe this image and explain "
            "the important information visible in it."
        )

    # --------------------------------------------------------
    # Gemini visual analysis
    # --------------------------------------------------------

    try:

        answer = generate_image_answer(
            file_bytes=file_bytes,
            mime_type=mime_type,
            question=user_question
        )

        return f"""
🖼️ Image Analysis

Filename: {filename}

Image type: {mime_type}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ Your Question

{user_question}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 IntelliVoice AI Answer

{answer}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Image analyzed using Gemini vision.
""".strip()

    except Exception as e:

        print("=" * 60)
        print("GEMINI IMAGE ANALYSIS ERROR")
        print("=" * 60)

        print(
            f"Error type: {type(e).__name__}"
        )

        print(
            f"Error     : {repr(e)}"
        )

        print("=" * 60)

        return f"""
🖼️ Image uploaded successfully.

Filename: {filename}

Image type: {mime_type}

Image size: {len(file_bytes)} bytes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Image understanding failed

The image reached IntelliVoice AI,
but Gemini could not analyze it right now.

Reason:
{str(e)}

Please check your Gemini API key,
internet connection, and Gemini API quota.
""".strip()


# ============================================================
# MAIN FILE ANALYSIS
# ============================================================

def analyze_file(
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    question: Optional[str] = None
) -> str:

    if mime_type in ALLOWED_PDF_TYPES:

        return analyze_pdf(
            file_bytes=file_bytes,
            filename=filename,
            question=question
        )

    if mime_type in ALLOWED_IMAGE_TYPES:

        return analyze_image(
            file_bytes=file_bytes,
            filename=filename,
            mime_type=mime_type,
            question=question
        )

    return (
        "Unsupported file type. "
        "Please upload a PDF, JPG, PNG, "
        "or WebP image."
    )