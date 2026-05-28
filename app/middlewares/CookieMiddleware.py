from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class CookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.agreed = request.cookies.get("agreed", None)

        response = await call_next(request)

        return response
