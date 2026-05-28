import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates/")


class DeviceDefinitionMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        user_agent = request.headers.get("user-agent", "")
        is_mobile = bool(
            re.search(r"Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile", user_agent, re.I))

        if not is_mobile:
            return templates.TemplateResponse(
                "errors/mobile-only.html",
                {
                    "request": request,
                },
                status_code=403,
            )
        response = await call_next(request)
        return response
