from fastapi import Request, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import User
from app.utils.flash import set_flash

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db


def require_roles(roles: list[str]):
    async def checker(
        request: Request,
        user: User = Depends(get_user),
    ):
        if user.role.name not in roles:
            await set_flash(
                request=request,
                messages=["У вас недостаточно прав!"],
                category="warning",
            )
            raise HTTPException(status_code=302, headers={"Location": "/home"})
        return user

    return checker


async def get_user(
        request: Request,
        db: AsyncSession = Depends(get_async_db),
) -> User:
    user = request.state.user

    if not user:
        request.session["next_url"] = str(request.url)
        raise HTTPException(status_code=302, headers={"Location": "/login"})

    stmt = select(User).where(User.id == user.id).options(selectinload(User.role))
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user:
        request.session["next_url"] = str(request.url)
        raise HTTPException(status_code=302, headers={"Location": "/login"})

    return user


async def user_or_guest(request: Request) -> User:
    return request.state.user if request.state.user else None


async def authorized_user(request: Request) -> None:
    if request.state.user:
        raise HTTPException(status_code=302, headers={"Location": "/home"})
