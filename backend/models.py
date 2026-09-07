from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

DifficultyLevel = str
TutorMode = Literal["learn", "hint", "challenge", "quiz", "review", "chat"]

class ChatMessage(BaseModel):
    id: Optional[str] = None
    role: Literal["user", "assistant", "system"]
    content: str
    followups: Optional[List[str]] = None
    created_at: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    mode: str = "learn"
    difficulty: str = "general"
    history: List[ChatMessage] = Field(default_factory=list)
    topic: Optional[str] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    mode: str = "learn"
    difficulty: str = "general"
    suggested_followups: List[str] = Field(default_factory=list)
    conversation_id: Optional[str] = None

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Chat"
    difficulty: str = "general"

class ConversationSummary(BaseModel):
    id: str
    title: str
    difficulty: str = "general"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ConversationDetail(BaseModel):
    id: str
    title: str
    difficulty: str = "general"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)

class ExplainRequest(BaseModel):
    code: str
    language: str = "python"
    difficulty: DifficultyLevel = "beginner"

class LineExplanation(BaseModel):
    line_number: int
    code: str
    explanation: str

class ExplainResponse(BaseModel):
    language: str
    difficulty: DifficultyLevel
    summary: str
    line_by_line: List[LineExplanation]
    concepts: List[str]
    time_complexity: str
    space_complexity: str
    tutor_tips: List[str]

class DebugRequest(BaseModel):
    code: str
    language: str = "python"
    error_message: Optional[str] = None
    difficulty: DifficultyLevel = "beginner"

class DebugResponse(BaseModel):
    language: str
    difficulty: DifficultyLevel
    has_bug: bool
    error_type: str
    root_cause: str
    fixed_code: str
    explanation: str
    prevention_tips: List[str]
