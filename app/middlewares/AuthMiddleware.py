from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.database import AsyncSessionLocal
from app.models import User
from app.redis import redis_client
from app.settings import settings
from app.utils.jwt_tokens import (
    ALGORITHM,
    create_access_token,
    create_refresh_token,
    REFRESH_TTL, is_blacklisted
)


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        user_id = None

        new_access = None
        new_refresh = None

        # =========================
        # 🔎 GET TOKENS
        # =========================
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header[7:]
            refresh_token = request.headers.get("X-Refresh-Token")

        # =========================
        # 🔐 ACCESS CHECK
        # =========================
        if access_token:
            try:
                payload = jwt.decode(
                    access_token,
                    settings.SECRET_KEY,
                    algorithms=[ALGORITHM]
                )

                jti = payload["jti"]

                if await is_blacklisted(jti):
                    response = JSONResponse(
                        status_code=401,
                        content={"detail": "Token has been revoked"}
                    )
                    response.delete_cookie("access_token")
                    response.delete_cookie("refresh_token")

                    return response

                user_id = int(payload["sub"])

            except ExpiredSignatureError:
                pass
            except JWTError:
                pass

        # =========================
        # 🔄 REFRESH FLOW (ROTATION)
        # =========================
        if not user_id and refresh_token:

            key = f"refresh:{refresh_token}"
            db_user_id = await redis_client.get(key)

            if db_user_id:
                user_id = int(db_user_id)

                # ⚠️ сначала создаём новый
                new_refresh = create_refresh_token()
                new_access = create_access_token(user_id)

                # кладём новый
                await redis_client.setex(
                    f"refresh:{new_refresh}",
                    REFRESH_TTL,
                    str(user_id)
                )

                # удаляем старый (после)
                await redis_client.delete(key)

        # =========================
        # 📦 SAVE USER
        # =========================

        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(User)
                    .options(selectinload(User.role))
                    .where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
        except Exception:
            user = None

        request.state.user = user

        response: Response = await call_next(request)

        # =========================
        # 🍪 SET TOKENS
        # =========================
        if new_access:
            response.set_cookie(
                "access_token",
                new_access,
                httponly=True,
            )

        if new_refresh:
            response.set_cookie(
                "refresh_token",
                new_refresh,
                httponly=True,
            )

        # =========================
        # 📱 API SUPPORT
        # =========================
        if new_access:
            response.headers["X-New-Access-Token"] = new_access

        if new_refresh:
            response.headers["X-New-Refresh-Token"] = new_refresh

        return response
