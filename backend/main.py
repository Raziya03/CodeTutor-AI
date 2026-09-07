import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Load local environment variables if .env exists
load_dotenv()

from models import (
    ChatRequest, ChatResponse,
    ExplainRequest, ExplainResponse,
    DebugRequest, DebugResponse,
    ConversationCreate, ConversationSummary, ConversationDetail
)
from tutor_engine import tutor_engine
from auth import get_current_user, get_optional_user
import database

app = FastAPI(
    title="Programming Tutor AI Chatbot API",
    description="Backend API powering interactive AI programming tutoring, code explanations, and debugging.",
    version="1.0.0"
)

# CORS configuration supporting local Vite, Vercel deployments, and previews
raw_origins = os.getenv("ALLOWED_ORIGINS", "*").strip()
if raw_origins == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Detect frontend static distribution path
def get_frontend_dist_path():
    candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "dist")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist")),
    ]
    for p in candidates:
        if os.path.exists(os.path.join(p, "index.html")):
            return p
    return candidates[0]

frontend_dist = get_frontend_dist_path()
assets_dist = os.path.join(frontend_dist, "assets")
if os.path.exists(assets_dist):
    app.mount("/assets", StaticFiles(directory=assets_dist), name="assets")


@app.get("/api/health")
def health_check():
    """Status probe reporting backend, AI model, and database readiness."""
    load_dotenv(override=True)
    return {
        "status": "online",
        "service": "Programming Tutor AI Chatbot API",
        "version": "1.0.0",
        "database_configured": database.is_db_configured(),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY", "").strip())
    }

@app.get("/api/auth/me")
def get_current_user_profile(user: Optional[Dict[str, Any]] = Depends(get_optional_user)):
    """Returns the authenticated user details, or guest status if unauthenticated."""
    if not user:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": user}

@app.post("/api/chat", response_model=ChatResponse)
def chat_with_tutor(
    req: ChatRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Conversational tutor endpoint calibrated to student difficulty level.
    If authenticated, seamlessly logs user and assistant turns to Supabase.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    conv_id = req.conversation_id

    # If user is authenticated, handle conversation persistence
    if current_user:
        user_id = current_user["id"]
        token = current_user.get("token")
        # If no active conversation specified, create a new one with a smart title
        if not conv_id:
            title = req.message.strip().replace("\n", " ")[:40]
            new_conv = database.create_conversation(user_id, title=title, difficulty=req.difficulty, token=token)
            if new_conv:
                conv_id = str(new_conv["id"])

        # Save user message to database
        if conv_id:
            database.save_message(conv_id, role="user", content=req.message, token=token)

    # Generate pedagogical reply (via OpenAI if key present, else built-in tutor)
    response = tutor_engine.chat(req)

    # Attach and persist assistant response if conversation exists
    if conv_id:
        response.conversation_id = conv_id
        if current_user:
            database.save_message(
                conv_id,
                role="assistant",
                content=response.reply,
                followups=response.suggested_followups,
                token=current_user.get("token")
            )

    return response

@app.get("/api/conversations", response_model=List[ConversationSummary])
def list_user_conversations(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Fetch all past chat threads belonging to the authenticated student."""
    conversations = database.list_conversations(current_user["id"], token=current_user.get("token"))
    return [
        ConversationSummary(
            id=str(c["id"]),
            title=c.get("title", "New Chat"),
            difficulty=c.get("difficulty", "general"),
            created_at=str(c.get("created_at", "")),
            updated_at=str(c.get("updated_at", ""))
        )
        for c in conversations
    ]

@app.post("/api/conversations", response_model=ConversationDetail)
def create_new_conversation(
    body: ConversationCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Start a fresh chat thread for the authenticated student."""
    conv = database.create_conversation(
        user_id=current_user["id"],
        title=body.title or "New Chat",
        difficulty=body.difficulty,
        token=current_user.get("token")
    )
    if not conv:
        raise HTTPException(status_code=500, detail="Failed to initialize conversation session.")

    return ConversationDetail(
        id=str(conv["id"]),
        title=conv.get("title", "New Chat"),
        difficulty=conv.get("difficulty", "general"),
        created_at=str(conv.get("created_at", "")),
        updated_at=str(conv.get("updated_at", "")),
        messages=[]
    )

@app.get("/api/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation_history(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve full message history for a specific conversation session."""
    conv = database.get_conversation(conversation_id, user_id=current_user["id"], token=current_user.get("token"))
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return ConversationDetail(
        id=str(conv["id"]),
        title=conv.get("title", "Chat"),
        difficulty=conv.get("difficulty", "general"),
        created_at=str(conv.get("created_at", "")),
        updated_at=str(conv.get("updated_at", "")),
        messages=conv.get("messages", [])
    )

@app.delete("/api/conversations/{conversation_id}")
def remove_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a conversation thread permanently."""
    success = database.delete_conversation(conversation_id, user_id=current_user["id"], token=current_user.get("token"))
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete conversation.")
    return {"message": "Conversation deleted successfully", "id": conversation_id}

@app.post("/api/explain", response_model=ExplainResponse)
def explain_code(req: ExplainRequest):
    """Line-by-line code explanation, concepts, and complexity analysis."""
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
    return tutor_engine.explain_code(req)

@app.post("/api/debug", response_model=DebugResponse)
def debug_code(req: DebugRequest):
    """Diagnose bugs, explain root causes, and provide corrected code."""
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
    return tutor_engine.debug_code(req)

@app.get("/{full_path:path}")
def serve_spa(full_path: str = ""):
    """Serve React frontend static build and handle single page application routing."""
    # Do not intercept unmatched /api routes
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="API endpoint not found.")

    # Check if a specific file exists in the frontend dist directory (e.g. favicon.svg)
    file_path = os.path.join(frontend_dist, full_path)
    if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    # Return index.html for all other routes
    index_html = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)

    return {
        "message": "Programming Tutor AI Backend is Running!",
        "health_check": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

