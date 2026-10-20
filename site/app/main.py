from __future__ import annotations

import contextlib
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.routing import Route

from .config import Settings
from .mcp_server import build_mcp, transport_security
from .services import Services
from .web import TEMPLATES, build_router

STATIC_DIR = Path(__file__).parent / "static"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    services = Services.create(settings)
    mcp = build_mcp(services)
    # Stateless + JSON responses: no sticky sessions needed, proxy-friendly on App Service.
    mcp_http = mcp.streamable_http_app(
        streamable_http_path="/mcp", stateless_http=True, json_response=True,
        transport_security=transport_security(services),
    )

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        async with mcp.session_manager.run():
            yield

    app = FastAPI(title="Model Mondays", lifespan=lifespan, docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json")
    app.state.services = services
    app.state.mcp = mcp
    app.include_router(build_router(services))
    for route in mcp_http.routes:
        if isinstance(route, Route) and route.path == "/mcp":
            app.router.routes.append(route)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/banners", StaticFiles(directory=settings.data_dir / "banners", check_dir=False), name="banners")

    @app.exception_handler(StarletteHTTPException)
    async def html_errors(request: Request, exc: StarletteHTTPException):
        wants_html = "text/html" in request.headers.get("accept", "") and not request.url.path.startswith(("/api", "/mcp"))
        if wants_html and exc.status_code in (401, 404):
            return TEMPLATES.TemplateResponse(
                request, "error.html",
                {"settings": settings, "seasons": services.data.seasons(), "status": exc.status_code,
                 "detail": exc.detail, "active": None, "is_admin": False, "epoch": "", "now": ""},
                status_code=exc.status_code,
            )
        return await http_exception_handler(request, exc)

    return app


app = create_app()
