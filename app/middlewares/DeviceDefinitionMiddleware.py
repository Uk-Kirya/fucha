import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates/")


class DeviceDefinitionMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        user_agent = request.headers.get("user-agent", "")
        is_mobile = bool(
            re.search(r"Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile", user_agent, re.I))

        if request.url.path == '/mobile-only':
            if is_mobile:
                return RedirectResponse("/", status_code=303)
            response = await call_next(request)
            return response

        # if not is_mobile:
        #     return RedirectResponse(
        #         url='/mobile-only',
        #         status_code=303,
        #     )

        response = await call_next(request)
        return response
