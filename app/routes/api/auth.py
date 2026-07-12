from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models import User
from app.redis import redis_client
from app.schemas.login_schema import LoginSchema
from app.settings import settings
from app.utils.jwt_tokens import create_access_token, create_refresh_token, REFRESH_TTL, ALGORITHM, blacklist_token
from app.utils.security import verify_password

from jose import jwt, JWTError
from datetime import datetime, timezone

auth = APIRouter(
    include_in_schema=True,
    prefix="/api/v1",
    tags=["API Auth"]
)


@auth.get(
    path="/test",
    summary="Тестовый route"
)
async def test_api(
        request: Request,
) -> JSONResponse:
    """
    Тестируем передачу данных на приложение SWIFT
    :param request: Request Object
    :return:
    """

    sessions = {
        "data": {
            "id": 1,
            "name": "Kirill",
            "age": 34,
            "city": "Sochi",
            "email": "udarnik.kirill@gmail.com"
        },
    }

    return JSONResponse(content=sessions)


@auth.post(
    path="/auth/login",
    summary="Логирование в приложении",
    response_class=JSONResponse
)
async def login(
        request: Request,
        data: LoginSchema,
        db: AsyncSession = Depends(get_async_db),
) -> JSONResponse:
    """
    Вводим логин и пароль, и авторизовываемся. Получаем токен и сохраняем его у себя
    :param data: Data from request
    :param request: Request Object
    :param db: DB Session Object
    :return: JsonResponse
    """

    errors = {}

    email = data.email
    password = data.password

    if email.strip() != '':
        if '@' not in email:
            errors['Incorrect Email'] = True
    else:
        errors['E-mail not entered'] = True

    if password.strip() == '':
        errors['Password not entered'] = True

    if errors:
        return JSONResponse(
            content={
                "success": False,
                "errors": errors
            },
            status_code=400
        )

    existing_user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()

    if not existing_user:
        return JSONResponse(
            content={
                "success": False,
                "errors": {
                    "email": "Пользователь не найден"
                }
            },
            status_code=404
        )

    if not existing_user.is_active:
        return JSONResponse(
            content={
                "success": False,
                "errors": {
                    "email": "Аккаунт деактивирован"
                }
            },
            status_code=403
        )

    if not verify_password(password, existing_user.hashed_password):
        return JSONResponse(
            content={
                "success": False,
                "errors": {
                    "password": "Неверный пароль"
                }
            },
            status_code=401
        )

    access = create_access_token(int(existing_user.id))
    refresh = create_refresh_token()

    await redis_client.setex(f"refresh:{refresh}", REFRESH_TTL, str(existing_user.id))

    return JSONResponse(
        content={
            "success": True,
            "access_token": access,
            "refresh_token": refresh
        },
        status_code=200
    )


@auth.post(
    path="/auth/logout",
    summary="Разлогирование из приложения",
    response_class=JSONResponse
)
async def logout(
        request: Request
) -> JSONResponse:
    """
    Разлогирование. Удаление всех redis сессий, а токен попадает в black-list
    :param request:
    :return:
    """

    auth_header = request.headers.get("Authorization")
    refresh_token = request.headers.get("X-Refresh-Token")

    access_token = None

    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header[7:]

    if refresh_token:
        await redis_client.delete(
            f"refresh:{refresh_token}"
        )

    if access_token:

        try:

            payload = jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            print("PAYLOAD:", payload)

            jti = payload.get("jti")
            exp = payload.get("exp")

            if jti and exp:

                now = datetime.now(timezone.utc).timestamp()

                ttl = int(exp - now)

                if ttl > 0:
                    await blacklist_token(
                        jti,
                        ttl
                    )

        except JWTError as e:
            print("JWT ERROR:", e)

    return JSONResponse(
        content={
            "success": True
        },
        status_code=200
    )


@auth.post(
    path="/auth/reset-password",
    summary="Отправление ссылки сброса пароля на почту",
    response_class=JSONResponse
)
async def reset_password(
        request: Request
) -> JSONResponse:
    """
    Отправляем 6-ти значный код на почту
    :param request:
    :return:
    """


@auth.post(
    path="/auth/create-new-password",
    summary="Создание и подтверждение нового пароля",
    response_class=JSONResponse
)
async def confirm_new_password(
        request: Request
) -> JSONResponse:
    """
    Вводим 6-ти значный код с почты, и потом вводим новый пароль
    :param request:
    :return:
    """
