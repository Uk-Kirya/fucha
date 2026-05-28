from app.database import get_async_db
from app.models import User
from app.settings import templates

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

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
        db: AsyncSession = Depends(get_async_db),
) -> HTMLResponse:
    """
    Страница панели администрирования
    """

    return templates.TemplateResponse(
        "admin/home.html",
        {
            "request": request,
        },
    )
