import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.templating import Jinja2Templates

from app.logs.logger_config import logger

templates = Jinja2Templates(directory="app/templates/")


class LoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:

        start_time = time.time()

        ip = request.client.host if request.client else "-"
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent", "-")

        try:

            response = await call_next(request)

            process_time = round(
                (time.time() - start_time) * 1000,
                2
            )

            logger.bind(
                ip=ip,
                method=method,
                path=path,
                status=response.status_code,
                process_time=process_time,
                user_agent=user_agent,
            ).info(
                "Request completed"
            )

            # ==========================
            # API НЕ ТРОГАЕМ
            # ==========================

            if request.url.path.startswith("/api/"):
                return response

            # ==========================
            # WEB ERROR PAGES
            # ==========================

            if response.status_code == 429:
                return templates.TemplateResponse(
                    "client/errors/429.html",
                    {
                        "request": request,
                        "retry_after": response.headers.get(
                            "Retry-After"
                        ),
                    },
                    status_code=429,
                )

            if response.status_code == 403:
                return templates.TemplateResponse(
                    "client/errors/403.html",
                    {
                        "request": request,
                    },
                    status_code=403,
                )

            if 400 <= response.status_code < 500:
                agreed = getattr(
                    request.state,
                    "agreed",
                    False
                )

                return templates.TemplateResponse(
                    "client/errors/400.html",
                    {
                        "request": request,
                        "agreed": agreed,
                    },
                    status_code=response.status_code,
                )

            return response

        except Exception as e:

            logger.exception(
                "Unhandled server error"
            )

            # API ошибки возвращаем JSON

            if request.url.path.startswith("/api/"):
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "errors": {
                            "server": "Internal server error"
                        }
                    }
                )

            agreed = getattr(
                request.state,
                "agreed",
                False
            )

            return templates.TemplateResponse(
                "client/errors/500.html",
                {
                    "request": request,
                    "agreed": agreed,
                    "error": e,
                },
                status_code=500,
            )
