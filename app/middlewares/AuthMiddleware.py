from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.database import AsyncSessionLocal
from app.models import User
from app.settings import settings
from app.utils.jwt_tokens import (
    ALGORITHM,
    is_blacklisted,
)


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        user = None

        access_token = request.cookies.get("access_token")

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header[7:]

        if access_token:
            try:
                payload = jwt.decode(
                    access_token,
                    settings.SECRET_KEY,
                    algorithms=[ALGORITHM]
                )

                jti = payload.get("jti")

                if jti and await is_blacklisted(jti):
                    request.state.user = None
                    return await call_next(request)

                user_id = int(payload["sub"])

                async with AsyncSessionLocal() as db:
                    result = await db.execute(
                        select(User)
                        .options(selectinload(User.role))
                        .where(User.id == user_id)
                    )

                    user = result.scalar_one_or_none()

            except JWTError:
                user = None

        request.state.user = user

        response = await call_next(request)

        return response
