from datetime import datetime

from app.domain.token.exceptions import TokenExpired


class TokenDomain:
    def __init__(self, token_obj):
        self._token = token_obj

    @property
    def user_id(self) -> int:
        return self._token.user_id

    @property
    def token(self) -> str:
        return self._token.token

    @property
    def expires_at(self) -> bool:
        return self._token.expires_at < datetime.now()

    @property
    def used(self) -> bool:
        return self._token.used

    def validate(self):
        if self.expires_at:
            raise TokenExpired('Токен устарел!')

        if self.used:
            raise TokenExpired('Токен уже использован!')
