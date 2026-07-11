from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from app.models import User
from app.schemas.user_schema import UserWithRole
from app.settings import templates
from app.utils.get_current_user import user_or_guest

challenges = APIRouter(
    include_in_schema=False,
    tags=["Список всех челленджей"]
)


@challenges.get(
    path="/challenges",
    response_class=HTMLResponse,
    name='challenges',
    summary="Список всех челленджей"
)
async def home_page(
        request: Request,
        user: User = Depends(user_or_guest),
) -> HTMLResponse or RedirectResponse:
    """
    Список всех челленджей
    :param user: User or Guest object
    :param request: Request object
    :return: HTMLResponse
    """

    return templates.TemplateResponse(
        "client/pages/challenges.html",
        {
            "user": UserWithRole.model_validate(user) if user else None,
            "request": request,
        },
    )
