from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.settings import templates

web = APIRouter(
    include_in_schema=False,
    tags=["Главная страница"]
)


@web.get(
    path="/",
    response_class=HTMLResponse,
    name="home_page",
    summary="Главная страница"
)
async def home_page(
        request: Request,
) -> HTMLResponse or RedirectResponse:
    """
    Главная страница
    :param request: Request object
    :return: HTMLResponse
    """

    return templates.TemplateResponse(
        "web/home.html",
        {
            "request": request,
        },
    )
