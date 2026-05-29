from fastapi import Request, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.database import get_async_db
from app.models import User
from app.utils.flash import set_flash, set_form_data
from app.utils.security import verify_password


@limiter.limit('5/minute')
async def user_exists(
        request: Request,
        db: AsyncSession = Depends(get_async_db)
) -> User | HTTPException:

    form_data = await request.form()
    email = form_data.get("email")
    password = form_data.get("password")

    await set_form_data(
        request=request,
        data={
            "email": email or "",
            "password": password or ""
        }
    )

    messages = []

    if email.strip() != '':
        if '@' not in email:
            messages.append('E-mail не корректный!')
    else:
        messages.append('Необходимо ввести E-mail!')

    if password.strip() == '':
        messages.append("Необходимо ввести пароль!")

    if messages:
        await set_flash(
            request=request,
            messages=messages,
            category="warning"
        )
        raise HTTPException(
            status_code=303,
            headers={"Location": "/login"}
        )

    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        await set_flash(
            request,
            ["Пользователь с таким E-mail не существует!"],
            category="warning",
        )
        raise HTTPException(
            status_code=303,
            headers={"Location": "/login"}
        )

    if not verify_password(password, user.hashed_password):
        await set_flash(
            request,
            ["Пароль неверный!"],
            category="warning",
        )
        raise HTTPException(
            status_code=303,
            headers={"Location": "/login"}
        )

    if not user.is_active:
        await set_flash(
            request,
            ["Ваш аккаунт был заблокирован. Обратитесь к администратору!"],
            category="warning",
        )
        raise HTTPException(
            status_code=303,
            headers={"Location": "/login"}
        )

    return user
