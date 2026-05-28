from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class FlashMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        flash = request.session.pop("flash", None)
        request.state.flash = flash

        form_data = request.session.pop("form_data", {})
        request.state.form_data = form_data

        response = await call_next(request)

        return response
