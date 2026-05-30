from starlette.responses import RedirectResponse

from app.database import get_async_db
from app.models import User
from app.redis import redis_client
from app.schemas.user_schema import UserWithRole
from app.settings import templates, settings

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.logs.logger_config import logger
from app.utils.flash import set_flash
from app.utils.get_current_user import require_roles

home = APIRouter(
    include_in_schema=True,
    prefix="/admin",
    tags=["Панель администрирования"]
)


@home.get(
    path="/",
    response_class=HTMLResponse,
    summary="Админ.панель сайта"
)
async def get_admin(
        request: Request,
        user: User = Depends(require_roles(["admin"])),
) -> HTMLResponse or RedirectResponse:
    """
    Страница панели администрирования
    """

    refresh = request.cookies.get("refresh_token")

    return templates.TemplateResponse(
        "admin/home.html",
        {
            "request": request,
            "user": UserWithRole.model_validate(user),
            "access": request.cookies.get("access_token", None),
            "refresh": request.cookies.get("refresh_token", None),
            "refresh_redis": await redis_client.get(f"refresh:{refresh}"),
        },
    )
