import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.redis import redis_client
from app.settings import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


ACCESS_TTL = 15
REFRESH_TTL = 7 * 24 * 3600


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "access",
        "jti": str(uuid.uuid4()),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TTL),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token() -> str:
    return str(uuid.uuid4())


async def blacklist_token(jti: str, exp_seconds: int) -> None:
    await redis_client.setex(f"blacklist:{jti}", exp_seconds, '1')


async def is_blacklisted(jti: str) -> bool:
    return await redis_client.get(f"blacklist:{jti}") is not None
