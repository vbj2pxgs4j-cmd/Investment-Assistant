"""FastAPI Entrypoint for Mutual Fund FAQ Assistant."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.endpoints import get_chat_service, router as api_router
from backend.app.core.config import get_settings
from backend.app.core.logging import get_logger, setup_logging

settings = get_settings()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifespan context manager."""
    setup_logging(settings.log_level)
    logger.info("Starting %s v%s in %s mode", settings.app_name, settings.app_version, settings.environment)

    # Pre-warm vector store index on startup
    try:
        service = get_chat_service()
        service.initialize()
        logger.info("Vector store index initialized and ready for queries.")
    except Exception as e:
        logger.warning("Vector store auto-initialization deferred: %s", e)

    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Compliance-first, facts-only RAG assistant for HDFC Mutual Fund schemes.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(api_router)

# Mount Frontend Static Web Application
from pathlib import Path
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

static_dir = Path(__file__).resolve().parent / "static"
frontend_dist_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"

# Serve backend/static or built frontend/dist at /app
if static_dir.exists():
    app.mount("/app", StaticFiles(directory=str(static_dir), html=True), name="static_app")
elif frontend_dist_dir.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dist_dir), html=True), name="frontend_dist_app")


# Centralized Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Standardized validation error handler."""
    raw_errors = exc.errors()
    error_msg = raw_errors[0].get("msg", "Invalid request parameter") if raw_errors else "Validation error"
    safe_errors = []
    for err in raw_errors:
        safe_errors.append({
            "type": str(err.get("type", "value_error")),
            "loc": [str(x) for x in err.get("loc", [])],
            "msg": str(err.get("msg", "")),
            "input": str(err.get("input", "")),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": error_msg,
            "error_type": "validation_error",
            "errors": safe_errors,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all global exception handler."""
    logger.exception("Unhandled server exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred while processing the request.",
            "error_type": "internal_error",
        },
    )


@app.get("/", tags=["General"])
async def root(request: Request):
    """Root entrypoint returning UI for browser requests or JSON metadata for API clients."""
    accept_header = request.headers.get("accept", "")
    static_index = static_dir / "index.html"
    
    # If a browser requests the root URL, serve the interactive web application
    if "text/html" in accept_header and static_index.exists():
        return FileResponse(str(static_index), media_type="text/html")

    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "online",
        "web_ui": "/app",
        "docs": "/docs",
        "api_v1": "/api/v1",
        "disclaimer": settings.default_disclaimer,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug or settings.environment == "development",
    )
