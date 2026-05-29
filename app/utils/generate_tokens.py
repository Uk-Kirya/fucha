from fastapi import Request, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.database import get_async_db
from app.domain.token.csrf import CsrfTokenDomain
from app.domain.token.exceptions import TokenInvalid
from app.domain.token.token import TokenDomain
from app.models import PasswordResetToken, User
from app.utils.flash import set_flash


async def csrf_token_gen(request: Request) -> str:
    """
    Генерируем CSRF токен для использования в формах
    :param request: Request instance
    """

    token = CsrfTokenDomain.generate()
    request.session["csrf_token"] = token

    return token


async def csrf_token_check(
        request: Request
) -> None:
    """
    Валидация CSRF токена
    """

    # Берем данные из формы, переданной в объект запроса
    form_data = await request.form()

    # из данных извлекаем токен по ключу
    csrf_token = form_data.get("csrf_token")

    # берем токен из сессии
    session_token = request.session.get("csrf_token")

    try:
        CsrfTokenDomain.validate(csrf_token, session_token)
    except TokenInvalid:
        await set_flash(
            request=request,
            messages=["CSRF токен невалиден!"],
            category="warning"
        )

        next_url = request.headers.get('Referer')

        raise HTTPException(status_code=302, headers={"Location": next_url})


async def password_token_generate(
        user: User,
) -> PasswordResetToken:
    return PasswordResetToken.generate(user.id)


async def check_token_password_reset(
        request: Request,
        db: AsyncSession = Depends(get_async_db)
) -> str | HTTPException:
    """
    Валидация токена сброса Пароля или подтверждения E-mail
    """

    token = request.query_params.get("token")

    if not token:
        await set_flash(
            request=request,
            messages=['Токен отсутствует в ссылке!'],
            category="warning"
        )
        raise HTTPException(status_code=303, headers={"Location": "/forgot-password"})

    stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
    token_obj = (await db.execute(stmt)).scalar_one_or_none()

    if not token_obj:
        await set_flash(
            request=request,
            messages=['Ссылка для сброса пароля недействительна!'],
            category="warning"
        )
        raise HTTPException(status_code=303, headers={"Location": "/forgot-password"})

    try:
        TokenDomain(token_obj=token_obj).validate()
    except TokenInvalid:
        await set_flash(
            request=request,
            messages=["Токен невалиден!"],
            category="warning"
        )
        raise HTTPException(status_code=303, headers={"Location": "/forgot-password"})

    return token


@limiter.limit('5/minute')
async def get_password_reset_token_obj(
        request: Request,
        db: AsyncSession = Depends(get_async_db),
) -> PasswordResetToken or HTTPException:

    form_data = await request.form()
    token = form_data.get("token")

    if not token:
        await set_flash(
            request=request,
            messages=['Токен отсутствует в форме!']
        )
        raise HTTPException(status_code=303, headers={"Location": "/forgot-password"})

    stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
    token_obj = (await db.execute(stmt)).scalar_one_or_none()

    if not token_obj:
        await set_flash(
            request=request,
            messages=['Такого токена не существует!'],
            category="warning"
        )
        raise HTTPException(status_code=303, headers={"Location": "/forgot-password"})

    try:
        TokenDomain(token_obj=token_obj).validate()
    except TokenInvalid:
        await set_flash(
            request=request,
            messages=["Токен невалиден!"],
            category="warning"
        )
        raise HTTPException(status_code=303, headers={"Location": "/forgot-password"})

    return token_obj
