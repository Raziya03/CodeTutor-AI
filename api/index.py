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
        path_override = (
            headers.get(b"x-matched-path", b"").decode("utf-8") or
            headers.get(b"x-forwarded-uri", b"").decode("utf-8") or
            headers.get(b"x-rewrite-url", b"").decode("utf-8")
        )
        if path_override:
            scope["path"] = path_override.split("?")[0]
        elif scope.get("path", "") in ["/api/index.py", "/api/index", "/api/"]:
            scope["path"] = "/api/health"
    await fastapi_app(scope, receive, send)
