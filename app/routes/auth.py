from datetime import datetime, timezone

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models import User
from app.redis import redis_client
from app.settings import templates, settings
from app.utils.flash import set_flash
from app.utils.generate_tokens import csrf_token_gen, csrf_token_check
from app.utils.jwt_tokens import create_access_token, create_refresh_token, ALGORITHM, blacklist_token, REFRESH_TTL
from app.utils.user_exists import user_exists

auth = APIRouter(
    include_in_schema=True,
    tags=["Авторизация / Регистрация"]
)


@auth.get(
    path="/",
    response_class=HTMLResponse,
    summary="Страница приветствие"
)
async def welcome_page(
        request: Request,
) -> HTMLResponse or RedirectResponse:
    """
    Страница приветствие
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
        csrf_token: str = Depends(csrf_token_gen)
) -> HTMLResponse:
    """
    Страница логирования. Вводим логин и пароль и отправляем на проверку форму
    :param request: Request object
    :param csrf_token: CSRF token
    :return: HTMLResponse
    """

    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "csrf_token": csrf_token,
        }
    )


@auth.post(
    path='/login',
    summary='Обработка формы логирования',
    response_class=HTMLResponse
)
async def get_login_page(
        request: Request,
        _: None = Depends(csrf_token_check),
        user: User = Depends(user_exists),
) -> RedirectResponse:
    """
    Проверка данных из формы и последующее логирование в приложении
    :param request: Request object
    :param user: User object
    :param _: Check CSRF Token from form
    :return: RedirectResponse
    """

    user_id = user.id

    access = create_access_token(user_id)
    refresh = create_refresh_token()

    await redis_client.setex(f"refresh:{refresh}", REFRESH_TTL, str(user_id))

    response = RedirectResponse(url='/admin', status_code=302)

    response.set_cookie("access_token", access, httponly=True)
    response.set_cookie("refresh_token", refresh, httponly=True)

    return response


@auth.get(
    path='/logout',
    summary="Разлогирование в приложении",
    response_class=RedirectResponse
)
async def logout(
        request: Request,
) -> RedirectResponse:
    """
    Разлогирование с приложения. Удаление всех токенов и блэк-лист для JWT
    :param request:
    :return: RedirectResponse
    """

    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if access_token:
        try:
            payload = jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"verify_aud": False}
            )

            jti = payload["jti"]
            expires = payload["exp"]

            if jti and expires:
                now = datetime.now(timezone.utc).timestamp()
                ttl = int(expires - now)
                await blacklist_token(jti, ttl)
        except JWTError:
            pass

    response = RedirectResponse(url='/login', status_code=302)
    await redis_client.delete(f"refresh:{refresh_token}")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    keys = await redis_client.keys("refresh:*")

    for key in keys:
        await redis_client.delete(key)

    return response


@auth.get(
    path='/mobile-only',
    summary='Только для мобильных устройств',
    response_class=HTMLResponse
)
async def get_mobile_only_page(
        request: Request,
) -> HTMLResponse:
    """
    Страница показывается, если на сайт зайти с компьютера (web-версия)
    :param request: Request object
    :return: HTMLResponse
    """
    return templates.TemplateResponse(
        "errors/mobile-only.html",
        {
            "request": request,
        }
    )


@auth.get(
    path="/cookies",
    summary="Просмотр Cookies"
)
async def redis_sessions(
        request: Request
) -> JSONResponse:
    sessions = {
        "cookies": {
            "access_token": request.cookies.get("access_token"),
            "refresh_token": request.cookies.get("refresh_token"),
        },
    }

    return JSONResponse(content=sessions)


@auth.get(
    path="/blacklist",
    summary='Просмотр Redis Blacklist'
)
async def get_blacklist():
    cursor = 0
    keys = []

    while True:
        cursor, partial = await redis_client.scan(
            cursor=cursor,
            match="blacklist:*",
            count=100
        )
        keys.extend(partial)

        if cursor == 0:
            break

    data = {}

    for key in keys:
        data[key] = await redis_client.get(key)

    return {"blacklist": data}


@auth.get(
    path="/refresh",
    summary='Просмотр Redis Refresh Tokens',
)
async def get_refresh():
    cursor = 0
    keys = []

    while True:
        cursor, partial = await redis_client.scan(
            cursor=cursor,
            match="refresh:*",
            count=100
        )
        keys.extend(partial)

        if cursor == 0:
            break

    data = {}

    for key in keys:
        data[key] = await redis_client.get(key)

    return {"refresh": data}
