from jose import jwt, JWTError

from app.database import get_async_db
from app.models import User
from app.redis import redis_client
from app.settings import templates, settings

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.logs.logger_config import logger

from app.utils.jwt_tokens import SECRET_KEY, ALGORITHM, is_blacklisted

admin = APIRouter(
    include_in_schema=True,
    prefix="/admin",
    tags=["Панель администрирования"]
)


@admin.get(
    path="/",
    response_class=HTMLResponse,
    summary="Админ.панель сайта"
)
async def get_admin(
        request: Request,
) -> HTMLResponse:
    """
    Страница панели администрирования
    """

    refresh = request.cookies.get("refresh_token")

    return templates.TemplateResponse(
        "admin/home.html",
        {
            "request": request,
            "user": request.state.user,
            "access": request.cookies.get("access_token", None),
            "refresh": request.cookies.get("refresh_token", None),
            "refresh_redis": await redis_client.get(f"refresh:{refresh}"),
        },
    )
