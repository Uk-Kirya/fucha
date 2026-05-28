from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request
from app.database import AsyncSessionLocal
from app.redis import redis_client
from app.models import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.settings import settings


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None

        session_id = request.cookies.get("session_id")

        clear_cookie = False

        if session_id:
            key = f"session_id:{session_id}"
            try:
                user_id = await redis_client.get(key)
            except Exception:
                user_id = None

            if user_id:
                try:
                    async with AsyncSessionLocal() as db:
                        result = await db.execute(
                            select(User)
                            .options(selectinload(User.role))
                            .where(User.id == int(user_id))
                        )
                        user = result.scalar_one_or_none()
                except Exception:
                    user = None

                if user and getattr(user, "is_active", True):
                    try:
                        await redis_client.expire(key, settings.SESSION_TTL)
                    except Exception:
                        pass
                    request.state.user = user
                else:
                    clear_cookie = True
                    try:
                        await redis_client.delete(key)
                    except Exception:
                        pass
            else:
                clear_cookie = True

        response: Response = await call_next(request)

        if clear_cookie:
            response.delete_cookie("session_id")
        return response
