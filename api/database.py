import os
from typing import Optional, List, Dict, Any
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
# Prefer service role key for backend operations to bypass RLS when authenticated by our auth.py
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    or os.getenv("SUPABASE_SERVICE_KEY", "").strip()
    or os.getenv("SUPABASE_ANON_KEY", "").strip()
    or os.getenv("SUPABASE_KEY", "").strip()
)

_client = None

def get_supabase_client(token: Optional[str] = None):
    """Initializes and returns the Supabase client, attaching user auth token if available."""
    global _client
    url = os.getenv("SUPABASE_URL", "").strip()
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.getenv("SUPABASE_SERVICE_KEY", "").strip()
        or os.getenv("SUPABASE_ANON_KEY", "").strip()
        or os.getenv("SUPABASE_KEY", "").strip()
    )

    if not url or not key:
        return None

    try:
        from supabase import create_client
        if _client is None:
            _client = create_client(url, key)
        
        # If a specific user JWT token is passed, authenticate postgrest with it
        if token:
            authenticated_client = create_client(url, key)
            authenticated_client.postgrest.auth(token)
            return authenticated_client
            
        return _client
    except Exception as e:
        print(f"[CodeTutor DB] Note: Could not initialize Supabase client: {e}")
        return None

def is_db_configured() -> bool:
    """Check if Supabase database configuration is present."""
    return get_supabase_client() is not None

def list_conversations(user_id: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all conversations for a specific user ordered by last updated."""
    client = get_supabase_client(token)
    if not client:
        return []

    try:
        response = (
            client.table("conversations")
            .select("id, title, difficulty, created_at, updated_at")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"[CodeTutor DB] Error listing conversations: {e}")
        return []

def create_conversation(user_id: str, title: str = "New Chat", difficulty: str = "general", token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Create a new conversation session for a user."""
    client = get_supabase_client(token)
    if not client:
        return None

    try:
        data = {
            "user_id": user_id,
            "title": title[:60],
            "difficulty": difficulty or "general",
        }
        response = client.table("conversations").insert(data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"[CodeTutor DB] Error creating conversation: {e}")
        return None

def get_conversation(conversation_id: str, user_id: Optional[str] = None, token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetch conversation details along with its messages."""
    client = get_supabase_client(token)
    if not client:
        return None

    try:
        query = client.table("conversations").select("*").eq("id", conversation_id)
        if user_id:
            query = query.eq("user_id", user_id)
        conv_res = query.execute()

        if not conv_res.data or len(conv_res.data) == 0:
            return None

        conv = conv_res.data[0]
        # Fetch associated messages
        msg_res = (
            client.table("messages")
            .select("id, role, content, followups, created_at")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .execute()
        )
        conv["messages"] = msg_res.data or []
        return conv
    except Exception as e:
        print(f"[CodeTutor DB] Error getting conversation: {e}")
        return None

def delete_conversation(conversation_id: str, user_id: str, token: Optional[str] = None) -> bool:
    """Delete a conversation session."""
    client = get_supabase_client(token)
    if not client:
        return False

    try:
        res = (
            client.table("conversations")
            .delete()
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .execute()
        )
        return True
    except Exception as e:
        print(f"[CodeTutor DB] Error deleting conversation: {e}")
        return False

def save_message(
    conversation_id: str,
    role: str,
    content: str,
    followups: Optional[List[str]] = None,
    token: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Save a user or assistant message to a conversation."""
    client = get_supabase_client(token)
    if not client:
        return None

    try:
        data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "followups": followups or []
        }
        res = client.table("messages").insert(data).execute()

        # Update updated_at timestamp on conversation
        try:
            client.table("conversations").update({
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", conversation_id).execute()
        except Exception:
            pass

        if res.data and len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        print(f"[CodeTutor DB] Error saving message: {e}")
        return None

def update_conversation_title(conversation_id: str, title: str, token: Optional[str] = None) -> bool:
    """Update the title of a conversation."""
    client = get_supabase_client(token)
    if not client:
        return False

    try:
        client.table("conversations").update({
            "title": title[:60]
        }).eq("id", conversation_id).execute()
        return True
    except Exception as e:
        print(f"[CodeTutor DB] Error updating conversation title: {e}")
        return False
