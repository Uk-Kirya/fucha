from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

api = APIRouter(
    include_in_schema=True,
    prefix="/api",
    tags=["API"]
)


@api.get(
    path="/v1/test",
    summary="Просмотр Cookies"
)
async def redis_sessions(
        request: Request
) -> JSONResponse:

    sessions = {
        "data": {
            "hello": "world",
        },
    }

    return JSONResponse(content=sessions)
