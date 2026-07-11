from datetime import datetime, timezone

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.domain.user.model import UserDomain
from app.models import User
from app.redis import redis_client
from app.settings import templates, settings
from app.utils.generate_tokens import csrf_token_gen, csrf_token_check
from app.utils.get_current_user import authorized_user
from app.utils.jwt_tokens import create_access_token, create_refresh_token, ALGORITHM, blacklist_token, REFRESH_TTL
from app.utils.user_exists import user_exists

auth = APIRouter(
    include_in_schema=False,
    tags=["Авторизация / Регистрация"]
)


@auth.get(
    path="/",
    response_class=HTMLResponse,
    name='welcome',
    summary="Страница приветствие"
)
async def welcome_page(
        request: Request,
        _: None = Depends(authorized_user),
) -> HTMLResponse or RedirectResponse:
    """
    Страница приветствие
    :param _: Check User
    :param request: Request object
    :return: HTMLResponse
    """

    return templates.TemplateResponse(
        "client/welcome.html",
        {
            "request": request,
        },
    )


@auth.get(
    path='/login',
    summary='Страница логирования',
    name='login',
    response_class=HTMLResponse
)
async def get_login_page(
        request: Request,
        csrf_token: str = Depends(csrf_token_gen),
        _: None = Depends(authorized_user),
) -> HTMLResponse:
    """
    Страница логирования. Вводим логин и пароль и отправляем на проверку форму
    :param _: Check User
    :param request: Request object
    :param csrf_token: CSRF token
    :return: HTMLResponse
    """

    return templates.TemplateResponse(
        "client/auth/login.html",
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
        db: AsyncSession = Depends(get_async_db),
) -> RedirectResponse:
    """
    Проверка данных из формы и последующее логирование в приложении
    :param db: AsyncSession
    :param request: Request object
    :param user: User object
    :param _: Check CSRF Token from form
    :return: RedirectResponse
    """

    user_id = user.id

    access = create_access_token(user_id)
    refresh = create_refresh_token()

    await redis_client.setex(f"refresh:{refresh}", REFRESH_TTL, str(user_id))

    UserDomain(user).set_last_login()
    await db.commit()

    next_url = request.session.pop("next_url", "/home")
    response = RedirectResponse(url=next_url, status_code=302)

    response.set_cookie("access_token", access, max_age=REFRESH_TTL, httponly=True, samesite="lax")
    response.set_cookie("refresh_token", refresh, max_age=REFRESH_TTL, httponly=True, samesite="lax")

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
                if now < expires:
                    await blacklist_token(jti, ttl)
        except JWTError:
            pass

    response = RedirectResponse(url='/login', status_code=302)
    await redis_client.delete(f"refresh:{refresh_token}")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

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
        "client/errors/mobile-only.html",
        {
            "request": request,
        }
    )


@auth.get(
    path="/registration",
    response_class=HTMLResponse,
    summary="Регистрация в приложении",
)
async def get_register(
        request: Request,
        csrf_token: str = Depends(csrf_token_gen),
        _: None = Depends(authorized_user),
) -> HTMLResponse or RedirectResponse:
    return templates.TemplateResponse(
        "client/auth/register.html",
        {
            "request": request,
            "csrf_token": csrf_token,
        },
    )
