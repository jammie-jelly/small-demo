from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from . import config
from .security import is_local

app = FastAPI(title="small-demo: proxy/XFF admin-gate repro")


class AdminGateMiddleware(BaseHTTPMiddleware):
    """Mirrors the clinic app's DocsGateMiddleware: /admin only for local peers."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/admin" and not is_local(request):
            return JSONResponse({"detail": "admin access requires a trusted network"}, status_code=403)
        return await call_next(request)


app.add_middleware(AdminGateMiddleware)

# Added LAST so it is OUTERMOST — rewrites scope["client"] from X-Forwarded-For
# before any gate/is_local check runs. Same ordering as the clinic app.
app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts=config.trusted_proxies,
)


@app.get("/whoami")
def whoami(request: Request):
    return {
        "client_host": request.client.host if request.client else None,
        "x_forwarded_for": request.headers.get("x-forwarded-for"),
        "is_local": is_local(request),
        "trusted_proxies": config.trusted_proxies,
    }


@app.get("/admin")
def admin():
    return {"ok": True, "message": "you are admin (request classified as local)"}
