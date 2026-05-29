import secrets

from app.domain.token.exceptions import TokenInvalid


class CsrfTokenDomain:

    @staticmethod
    def generate() -> str:
        return secrets.token_hex(16)

    @staticmethod
    def validate(form_token: str | None, session_token: str | None) -> None:
        if not form_token or not session_token or (form_token != session_token):
            raise TokenInvalid('CSRF токен невалиден!')
