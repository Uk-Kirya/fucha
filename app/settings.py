from datetime import datetime

from fastapi import Request
from pydantic_settings import BaseSettings, SettingsConfigDict

from starlette.templating import Jinja2Templates

from app.utils.filters import filters

from urllib.parse import quote_plus

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")


class Settings(BaseSettings):
    app_name: str = "Fucha Application"
    debug: bool = True

    SECRET_KEY: str
    SESSION_TTL: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    POSTGRES_EXTERNAL_PORT: int
    REDIS_EXTERNAL_PORT: int
    FASTAPI_EXTERNAL_PORT: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    @property
    def database_url(self) -> str:
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{password}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


settings = Settings()


def global_variables(request: Request):
    year = datetime.now().year
    flash = request.state.flash
    form_data = request.state.form_data
    agreed = request.state.agreed
    request_path = "/" + "/".join(request.url.path.split("/")[1:])

    return {
        "year": year,
        "flash": flash,
        "form_data": form_data,
        "agreed": agreed,
        "r_path": request_path,
    }


templates = Jinja2Templates(directory="app/templates")

for name, func in filters.items():
    templates.env.filters[name] = func

templates.context_processors.append(global_variables)
