# ============================================================
# INTELLIVOICE AI - MAIN FASTAPI APPLICATION
# ============================================================

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback


# ============================================================
# IMPORT BACKEND MODULES
# ============================================================

try:
    from backend.agent import run_agent
    print("✅ Agent imported successfully")
except Exception as e:
    print("❌ Agent import failed:", e)
    raise


try:
    from backend.file_analysis import analyze_file
    print("✅ File analysis imported successfully")
except Exception as e:
    print("❌ File analysis import failed:", e)
    raise


try:
    from backend.llm import generate_search_response
    print("✅ Search function imported successfully")
except Exception as e:
    print("❌ Search function import failed:", e)
    raise


try:
    from database.mongodb import (
        save_chat,
        get_chat_history,
        clear_chat_history
    )
    print("✅ MongoDB imported successfully")

except Exception as e:
    print("❌ MongoDB import failed:", e)
    raise


# ============================================================
# CONVERSATION MEMORY
# ============================================================

try:
    from backend.memory import save_memory, clear_memory
    print("✅ Conversation memory imported successfully")

except Exception as e:
    print("⚠️ Conversation memory unavailable:", e)
    save_memory = None
    clear_memory = None


# ============================================================
# ACTIVE DOCUMENT CONTEXT
# ============================================================

try:
    from backend.file_analysis import clear_active_document_context
    print("✅ Document context imported successfully")

except Exception as e:
    print("⚠️ Document context cleanup unavailable:", e)
    clear_active_document_context = None


# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="IntelliVoice AI",
    description="Intelligent AI Agent with Conversational Interaction",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "IntelliVoice AI Backend is running",
        "status": "online"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "IntelliVoice AI"
    }


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):

    print("\n" + "=" * 60)
    print("INTELLIVOICE AI CHAT")
    print("User message:", request.message)
    print("=" * 60)

    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    if not request.message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    message = request.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    # --------------------------------------------------------
    # Run AI Agent
    # --------------------------------------------------------

    try:

        result = run_agent(message)

        print("Agent result:", result)

        # Make sure result is a dictionary
        if not isinstance(result, dict):

            result = {
                "action": "direct",
                "response": str(result)
            }

        action = result.get(
            "action",
            "direct"
        )

        response = result.get(
            "response",
            "Sorry, I could not generate a response."
        )

        # Convert response safely to string
        if response is None:
            response = "Sorry, I could not generate a response."

        response = str(response)

        print("Agent action:", action)
        print("AI response:", response)

        # ----------------------------------------------------
        # Save chat to MongoDB
        # ----------------------------------------------------

        mongodb_status = "not_saved"

        try:

            save_result = save_chat(
                user_message=message,
                ai_response=response,
                action=action
            )

            if (
                isinstance(save_result, dict)
                and save_result.get("success") is True
            ):

                mongodb_status = "saved"

                print(
                    "✅ MongoDB: Chat saved successfully"
                )

            else:

                mongodb_status = "failed"

                print(
                    "⚠️ MongoDB: Chat was not saved"
                )

        except Exception as mongo_error:

            mongodb_status = "failed"

            print(
                "⚠️ MongoDB save exception:",
                mongo_error
            )

        # ----------------------------------------------------
        # Final response
        # ----------------------------------------------------

        final_response = {
            "success": True,
            "message": message,
            "response": response,
            "action": action,
            "mongodb": mongodb_status
        }

        print("Response:", final_response)
        print("=" * 60)

        return final_response

    except Exception as e:

        print("\n❌ CHAT ERROR")
        print(str(e))

        traceback.print_exc()

        return {
            "success": False,
            "message": message,
            "response": (
                "Sorry, something went wrong "
                "while processing your request."
            ),
            "action": "error",
            "mongodb": "not_saved",
            "error": str(e)
        }


# ============================================================
# PDF UPLOAD
# ============================================================

@app.post("/uploadPDF")
async def upload_pdf(
    file: UploadFile = File(...),
    question: str = Form("")
):

    print("\n" + "=" * 60)
    print("PDF UPLOAD")
    print("Filename:", file.filename)
    print("Content type:", file.content_type)
    print("Question:", question)
    print("=" * 60)

    try:

        # ----------------------------------------------------
        # Validate file type
        # ----------------------------------------------------

        if file.content_type != "application/pdf":

            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )

        # ----------------------------------------------------
        # Read file
        # ----------------------------------------------------

        file_data = await file.read()

        if not file_data:

            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )

        print(
            "PDF size:",
            len(file_data),
            "bytes"
        )

        # ----------------------------------------------------
        # Clean question
        # ----------------------------------------------------

        clean_question = question.strip()

        if not clean_question:
            clean_question = None

        print(
            "Question:",
            clean_question or "(none)"
        )

        # ----------------------------------------------------
        # Analyze PDF
        # ----------------------------------------------------

        result = analyze_file(
            file_bytes=file_data,
            filename=file.filename,
            mime_type=file.content_type,
            question=clean_question
        )

        print("PDF result:", result)

        # ----------------------------------------------------
        # Save question/answer to conversation memory
        # ----------------------------------------------------

        if (
            clean_question
            and save_memory
        ):

            try:

                save_memory(
                    clean_question,
                    result
                )

                print(
                    "✅ PDF question saved to memory"
                )

            except Exception as memory_error:

                print(
                    "⚠️ PDF memory save failed:",
                    memory_error
                )

        print("✅ PDF analysis completed")

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {
            "success": True,
            "filename": file.filename,
            "type": "pdf",
            "response": str(result)
        }

    except HTTPException:
        raise

    except Exception as e:

        print("\n❌ PDF ERROR:")
        print(str(e))

        traceback.print_exc()

        return {
            "success": False,
            "filename": file.filename,
            "type": "pdf",
            "response": (
                "Unable to analyze the PDF. "
                "Please check the file and try again."
            ),
            "error": str(e)
        }


# ============================================================
# IMAGE UPLOAD
# ============================================================

@app.post("/uploadImage")
async def upload_image(
    file: UploadFile = File(...),
    question: str = Form("")
):

    print("\n" + "=" * 60)
    print("IMAGE UPLOAD")
    print("Filename:", file.filename)
    print("Content type:", file.content_type)
    print("Question:", question)
    print("=" * 60)

    try:

        # ----------------------------------------------------
        # Allowed image formats
        # ----------------------------------------------------

        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ]

        if file.content_type not in allowed_types:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPG, PNG and WEBP "
                    "images are allowed."
                )
            )

        # ----------------------------------------------------
        # Read image
        # ----------------------------------------------------

        file_data = await file.read()

        if not file_data:

            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty."
            )

        print(
            "Image size:",
            len(file_data),
            "bytes"
        )

        # ----------------------------------------------------
        # Clean question
        # ----------------------------------------------------

        clean_question = question.strip()

        if not clean_question:
            clean_question = None

        print(
            "Question:",
            clean_question or "(none)"
        )

        # ----------------------------------------------------
        # Analyze image
        # ----------------------------------------------------

        result = analyze_file(
            file_bytes=file_data,
            filename=file.filename,
            mime_type=file.content_type,
            question=clean_question
        )

        print("Image result:", result)

        # ----------------------------------------------------
        # Save question/answer to memory
        # ----------------------------------------------------

        if (
            clean_question
            and save_memory
        ):

            try:

                save_memory(
                    clean_question,
                    result
                )

                print(
                    "✅ Image question saved to memory"
                )

            except Exception as memory_error:

                print(
                    "⚠️ Image memory save failed:",
                    memory_error
                )

        print("✅ Image analysis completed")

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {
            "success": True,
            "filename": file.filename,
            "type": "image",
            "response": str(result)
        }

    except HTTPException:
        raise

    except Exception as e:

        print("\n❌ IMAGE ERROR:")
        print(str(e))

        traceback.print_exc()

        return {
            "success": False,
            "filename": file.filename,
            "type": "image",
            "response": (
                "Unable to analyze the image. "
                "Please check the file and try again."
            ),
            "error": str(e)
        }


# ============================================================
# WEB SEARCH
# ============================================================

@app.post("/search")
def search(request: ChatRequest):

    print("\n" + "=" * 60)
    print("WEB SEARCH")
    print("Query:", request.message)
    print("=" * 60)

    # --------------------------------------------------------
    # Validate query
    # --------------------------------------------------------

    if not request.message:

        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    message = request.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    try:

        # ----------------------------------------------------
        # Generate search-based AI response
        # ----------------------------------------------------

        result = generate_search_response(
            message
        )

        return {
            "success": True,
            "query": message,
            "response": str(result),
            "action": "search"
        }

    except Exception as e:

        print("❌ SEARCH ERROR:", e)

        traceback.print_exc()

        return {
            "success": False,
            "query": message,
            "response": (
                "Unable to perform web search. "
                "Please try again."
            ),
            "action": "search",
            "error": str(e)
        }


# ============================================================
# LIVE SEARCH
# ============================================================

@app.post("/live")
def live(request: ChatRequest):

    print("\n" + "=" * 60)
    print("LIVE SEARCH")
    print("Query:", request.message)
    print("=" * 60)

    # --------------------------------------------------------
    # Validate query
    # --------------------------------------------------------

    if not request.message:

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    message = request.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    try:

        # ----------------------------------------------------
        # Get current web information
        # ----------------------------------------------------

        result = generate_search_response(
            message
        )

        return {
            "success": True,
            "query": message,
            "response": str(result),
            "action": "live"
        }

    except Exception as e:

        print("❌ LIVE SEARCH ERROR:", e)

        traceback.print_exc()

        return {
            "success": False,
            "query": message,
            "response": (
                "Unable to get live information. "
                "Please try again."
            ),
            "action": "live",
            "error": str(e)
        }


# ============================================================
# CHAT HISTORY
# ============================================================

@app.get("/history")
def history(limit: int = 50):

    print("\n" + "=" * 60)
    print("FETCHING CHAT HISTORY")
    print("Limit:", limit)
    print("=" * 60)

    # --------------------------------------------------------
    # Limit protection
    # --------------------------------------------------------

    if limit < 1:
        limit = 1

    if limit > 200:
        limit = 200

    try:

        chats = get_chat_history(limit)

        # Safety check
        if chats is None:
            chats = []

        if not isinstance(chats, list):
            chats = list(chats)

        print(
            "History records returned:",
            len(chats)
        )

        return {
            "success": True,
            "count": len(chats),
            "history": chats
        }

    except Exception as e:

        print("❌ HISTORY ERROR:", e)

        traceback.print_exc()

        return {
            "success": False,
            "count": 0,
            "history": [],
            "error": str(e)
        }


# ============================================================
# DELETE CHAT HISTORY
# ============================================================

@app.delete("/history")
def delete_history():

    print("\n" + "=" * 60)
    print("CLEARING CHAT HISTORY")
    print("=" * 60)

    try:

        result = clear_chat_history()

        # ----------------------------------------------------
        # Check MongoDB result
        # ----------------------------------------------------

        if (
            isinstance(result, dict)
            and result.get("success") is True
        ):

            deleted_count = result.get(
                "deleted_count",
                0
            )

            print(
                "✅ Deleted:",
                deleted_count,
                "records"
            )

            # ------------------------------------------------
            # Clear local conversation memory
            # ------------------------------------------------

            if clear_memory:

                try:

                    clear_memory()

                    print(
                        "✅ Conversation memory cleared"
                    )

                except Exception as memory_error:

                    print(
                        "⚠️ Memory clear failed:",
                        memory_error
                    )

            # ------------------------------------------------
            # Clear active document context
            # ------------------------------------------------

            if clear_active_document_context:

                try:

                    clear_active_document_context()

                    print(
                        "✅ Active document context cleared"
                    )

                except Exception as document_error:

                    print(
                        "⚠️ Document context clear failed:",
                        document_error
                    )

            return {
                "success": True,
                "message": (
                    "Chat history cleared successfully."
                ),
                "deleted_count": deleted_count
            }

        else:

            print(
                "⚠️ MongoDB history clear failed"
            )

            return {
                "success": False,
                "message": (
                    "Unable to clear chat history."
                ),
                "deleted_count": 0,
                "error": (
                    result.get("error")
                    if isinstance(result, dict)
                    else "Unknown MongoDB error"
                )
            }

    except Exception as e:

        print(
            "❌ DELETE HISTORY ERROR:",
            e
        )

        traceback.print_exc()

        return {
            "success": False,
            "message": (
                "Unable to clear chat history."
            ),
            "deleted_count": 0,
            "error": str(e)
        }


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():

    print("\n")

    print("=" * 60)
    print("🚀 INTELLIVOICE AI BACKEND STARTED")
    print("=" * 60)

    print("API      : http://127.0.0.1:8000")
    print("Docs     : http://127.0.0.1:8000/docs")
    print("Health   : http://127.0.0.1:8000/health")

    print("Chat     : POST /chat")
    print("PDF      : POST /uploadPDF")
    print("Image    : POST /uploadImage")
    print("Search   : POST /search")
    print("Live     : POST /live")

    print("History  : GET /history")
    print("Clear    : DELETE /history")

    print("=" * 60)
    print("✅ Backend ready")
    print("=" * 60)