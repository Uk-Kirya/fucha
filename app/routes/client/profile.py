from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from app.models import User
from app.schemas.user_schema import UserWithRole
from app.settings import templates
from app.utils import get_current_user
from app.utils.get_current_user import user_or_guest, get_user, require_roles

profile = APIRouter(
    include_in_schema=True,
    tags=["Профиль пользователя"]
)


@profile.get(
    path="/profile",
    response_class=HTMLResponse,
    name='profile',
    summary="Профиль пользователя"
)
async def home_page(
        request: Request,
        user: User = Depends(get_user),
) -> HTMLResponse or RedirectResponse:
    """
    Профиль пользователя
    :param user: User or Guest object
    :param request: Request object
    :return: HTMLResponse
    """

    return templates.TemplateResponse(
        "client/pages/profile.html",
        {
            "user": UserWithRole.model_validate(user),
            "request": request,
        },
    )
