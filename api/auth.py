import os
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status
import jwt
from database import get_supabase_client

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "").strip()

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and verifies a Supabase JWT access token.
    First tries Supabase auth API if client is available;
    Falls back to verifying with SUPABASE_JWT_SECRET;
    Falls back to unverified decoding for user payload if secret is omitted.
    """
    if not token:
        return None

    # Option 1: Verify via Supabase Auth API
    client = get_supabase_client()
    if client:
        try:
            user_response = client.auth.get_user(token)
            if user_response and user_response.user:
                u = user_response.user
                return {
                    "id": str(u.id),
                    "email": u.email,
                    "role": u.role or "authenticated",
                    "user_metadata": u.user_metadata or {},
                    "token": token
                }
        except Exception:
            pass

    # Option 2: Verify with SUPABASE_JWT_SECRET if configured
    if SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            return {
                "id": str(payload.get("sub")),
                "email": payload.get("email"),
                "role": payload.get("role", "authenticated"),
                "user_metadata": payload.get("user_metadata", {}),
                "token": token
            }
        except Exception as e:
            print(f"[CodeTutor Auth] JWT secret validation failed: {e}")
            return None

    # Option 3: Decode token without verification for development/testing
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
        sub = unverified.get("sub")
        if sub:
            return {
                "id": str(sub),
                "email": unverified.get("email"),
                "role": unverified.get("role", "authenticated"),
                "user_metadata": unverified.get("user_metadata", {}),
                "token": token
            }
    except Exception:
        pass

    return None

def extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    """Extract raw bearer token from Authorization header."""
    if not authorization:
        return None
    parts = authorization.strip().split(" ")
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None

def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """
    Dependency that extracts the authenticated user if token is present,
    or returns None for guest/unauthenticated requests.
    """
    token = extract_bearer_token(authorization)
    if not token:
        return None
    return decode_token(token)

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Dependency that enforces authentication. Raises 401 if missing or invalid.
    """
    user = get_optional_user(authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in with Google.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
