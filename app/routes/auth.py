from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.settings import templates

auth = APIRouter(
    include_in_schema=True,
    tags=["Авторизация / Регистрация"]
)


@auth.get(
    path="/",
    response_class=HTMLResponse,
    summary="Логирование в приложении"
)
async def welcome_page(
        request: Request,
) -> HTMLResponse or RedirectResponse:
    """
    Логирование в приложении
    :param request: Request object
    :return: HTMLResponse
    """

    return templates.TemplateResponse(
        "auth/welcome.html",
        {
            "request": request,
        },
    )


@auth.get(
    path='/login',
    summary='Страница логирования',
    response_class=HTMLResponse
)
async def get_login_page(
        request: Request,
        db: AsyncSession = Depends(get_async_db)
) -> HTMLResponse:
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
        }
    )
