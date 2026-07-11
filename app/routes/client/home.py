from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from app.models import User
from app.schemas.user_schema import UserWithRole
from app.settings import templates
from app.utils.get_current_user import user_or_guest

home = APIRouter(
    include_in_schema=False,
    tags=["Главная страница пользователя"]
)


@home.get(
    path="/home",
    response_class=HTMLResponse,
    name="home",
    summary="Главная страница пользователя"
)
async def home_page(
        request: Request,
        user: User = Depends(user_or_guest),
) -> HTMLResponse or RedirectResponse:
    """
    Главная страница пользователя
    :param user: User or Guest object
    :param request: Request object
    :return: HTMLResponse
    """

    return templates.TemplateResponse(
        "client/pages/home.html",
        {
            "user": UserWithRole.model_validate(user) if user else None,
            "request": request,
        },
    )
