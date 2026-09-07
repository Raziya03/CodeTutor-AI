import sys
import os

# Add backend directory to system path so imports inside backend work seamlessly on Vercel
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app as fastapi_app

async def app(scope, receive, send):
    if scope.get("type") == "http":
        headers = dict(scope.get("headers", []))
        matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
        if matched_path:
            scope["path"] = matched_path
        elif scope.get("path", "").endswith("/api/index.py"):
            scope["path"] = "/api"
    await fastapi_app(scope, receive, send)
