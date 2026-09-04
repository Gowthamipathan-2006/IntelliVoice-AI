from fastapi import FastAPI
from backend.schemas import ChatRequest, ChatResponse
from backend.llm import generate_response


app = FastAPI(
    title="IntelliVoice AI",
    description="Intelligent AI Agent with Conversational Interaction",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "IntelliVoice AI backend is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = generate_response(request.message)

    return ChatResponse(
        response=response
    )