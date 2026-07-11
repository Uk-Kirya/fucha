from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from starlette.requests import Request
from starlette.responses import JSONResponse

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Хэшируем пароль при создании form_data
    :param password: Password str
    :return: Hashed password str
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяем пароль, введенный в форме с паролем в базе данных пользователя
    :param plain_password: Password from form
    :param hashed_password: Password from User table
    :return: bool
    """
    return pwd_context.verify(plain_password, hashed_password)
