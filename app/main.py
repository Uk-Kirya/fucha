from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app import models
from app.core.limiter import limiter
from app.database import engine
from app.redis import redis_client

from app.routes import test, api
from app.routes.admin import home as admin_home

from app.settings import settings

from app.middlewares import (
    AuthMiddleware,
    CookieMiddleware,
    FlashMiddleware,
    LoggerMiddleware,
    AccessMiddleware
)

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

# Proxy headers
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
app.add_middleware(TrustedHostMiddleware, allowed_hosts="*")

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(FlashMiddleware)
app.add_middleware(LoggerMiddleware)
app.add_middleware(CookieMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
# app.add_middleware(AccessMiddleware)

# Роуты панели администрирования
app.include_router(admin_home)

# Роуты тестирования (Redis / Cookies / Session)
app.include_router(test)

# Роуты API
app.include_router(api.auth)

# Статика и загруженные файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    await redis_client.close()
