from datetime import datetime

from app.domain.user.exceptions import InvalidPassword
from app.models import User as UserORM
from app.utils.security import verify_password, hash_password


class UserDomain:
    """
    Доменная часть User-а
    """

    def __init__(self, orm_user: UserORM) -> None:
        self._user = orm_user

    @property
    def id(self):
        return self._user.id

    @property
    def email(self):
        return self._user.email

    @property
    def name(self):
        return self._user.name

    @property
    def is_active(self):
        return self._user.is_active

    @property
    def is_premium(self):
        return self._user.is_premium

    @property
    def is_vip(self):
        return self._user.is_vip

    @property
    def last_login(self):
        return self._user.last_login

    def set_name(self, value: str) -> None:
        self._user.name = value

    def set_email(self, value: str) -> None:
        self._user.email = value

    def set_photo(self, value: str) -> None:
        self._user.photo = value

    def set_last_login(self) -> None:
        self._user.last_login = datetime.now().replace(second=0, microsecond=0)

    def set_password(self, password_1: str, password_2: str) -> None:
        """
        Установка пароля при сбросе пароля через восстановление (через токен)
        """

        if password_1 and password_2:
            if password_1 == password_2:
                self._user.hashed_password = hash_password(password_1)
            else:
                raise InvalidPassword("Пароли должны совпадать!")
        else:
            raise InvalidPassword("Введите новый пароль!")

    def change_password(self, current_password: str | None, password_1: str, password_2: str) -> None:
        """
        Установка нового пароля c подтверждением текущего (как правило, из админки)
        """

        if not current_password:
            raise InvalidPassword("Необходимо ввести текущий пароль!")
        else:
            if not verify_password(current_password, self._user.hashed_password):
                raise InvalidPassword("Текущий пароль неверный!")

        if password_1 and password_2:
            if password_1 == password_2:
                self._user.hashed_password = hash_password(password_1)
            else:
                raise InvalidPassword("Пароли должны совпадать!")
        else:
            raise InvalidPassword("Введите новый пароль!")

    def activate_user(self, value: bool) -> None:
        self._user.is_active = value

    def activate_premium(self, value: bool) -> None:
        self._user.is_premium = value

    def activate_vip(self, value: bool) -> None:
        self._user.is_vip = value

    def verified_user(self, value: bool) -> None:
        self._user.is_verified = value

