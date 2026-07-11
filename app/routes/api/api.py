from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from app.utils.security import access

api = APIRouter(
    include_in_schema=True,
    prefix="/api/v1",
    tags=["API"]
)


@api.get(
    path="/test",
    summary="Просмотр Cookies"
)
async def redis_sessions(
        request: Request,
        _: None = Depends(access),
) -> JSONResponse:

    sessions = {
        "data": {
            "hello": "world",
        },
    }

    return JSONResponse(content=sessions)


@api.post("/auth")
async def auth(request: Request) -> JSONResponse:
    ...
