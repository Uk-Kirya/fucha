from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.redis import redis_client
from app.utils.filters import format_ttl

test = APIRouter(
    include_in_schema=True,
    prefix="/test",
    tags=["Тестирование (Redis / Cookies / Session)"]
)


@test.get(
    path="/cookies",
    summary="Просмотр Cookies",
    include_in_schema=False,
)
async def redis_sessions(
        request: Request
) -> JSONResponse:
    sessions = {
        "cookies": {
            "access_token": request.cookies.get("access_token"),
            "refresh_token": request.cookies.get("refresh_token"),
        },
    }

    return JSONResponse(content=sessions)


@test.get(
    path="/blacklist",
    summary='Просмотр Redis Blacklist'
)
async def get_blacklist():
    cursor = 0
    keys = []

    # Получаем все ключи blacklist
    while True:
        cursor, partial = await redis_client.scan(
            cursor=cursor,
            match="blacklist:*",
            count=100
        )
        keys.extend(partial)

        if cursor == 0:
            break

    data: Dict[str, Any] = {}
    now = datetime.now(timezone.utc).timestamp()

    for key in keys:
        # Получаем значение и TTL
        value = await redis_client.get(key)
        ttl = await redis_client.ttl(key)

        # Извлекаем jti
        jti = key.replace("blacklist:", "")

        # Рассчитываем время истечения (если TTL > 0)
        expires_at = None
        if ttl > 0:
            expires_at = datetime.fromtimestamp(now + ttl, tz=timezone.utc)

        data[key] = {
            "jti": jti,
            "value": value.decode('utf-8') if isinstance(value, bytes) else value,
            "ttl_seconds": ttl,
            "ttl_human": format_ttl(ttl),
            "is_active": ttl > 0,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "key": key
        }

    # Сортируем по TTL (скоро истекающие первыми)
    sorted_data = dict(sorted(
        data.items(),
        key=lambda x: x[1]["ttl_seconds"] if x[1]["ttl_seconds"] > 0 else 999999
    ))

    return {
        "total": len(data),
        "active_tokens": sum(1 for item in data.values() if item["is_active"]),
        "expired_tokens": sum(1 for item in data.values() if not item["is_active"]),
        "blacklist": sorted_data
    }


@test.get(
    path="/refresh",
    summary='Просмотр Redis Refresh Tokens',
)
async def get_refresh():
    cursor = 0
    keys = []

    while True:
        cursor, partial = await redis_client.scan(
            cursor=cursor,
            match="refresh:*",
            count=100
        )
        keys.extend(partial)

        if cursor == 0:
            break

    data = {}

    for key in keys:
        data[key] = await redis_client.get(key)

    return {"refresh": data}
