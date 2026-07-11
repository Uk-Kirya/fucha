from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.settings import settings
import jwt


API_KEY = settings.API_KEY
API_KEY_NAME = settings.API_KEY_NAME

PUBLIC_PATHS = [
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api",
    "/health",
]


class AccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        api_key = request.headers.get(API_KEY_NAME)
        if not api_key:
            return JSONResponse(
                content={
                    "error": "Missing API Key",
                    "message": f"{API_KEY_NAME} header is required"
                },
                status_code=401
            )

        if api_key != API_KEY:
            return JSONResponse(
                content={
                    "error": "Invalid API Key",
                    "message": "The provided API key is incorrect"
                },
                status_code=401
            )

        response = await call_next(request)
        return response
