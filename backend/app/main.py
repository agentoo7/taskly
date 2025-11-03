"""Main FastAPI application."""

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.auth import router as auth_router
from app.api.boards import router as boards_router
from app.api.cards import router as cards_router
from app.api.health import router as health_router
from app.api.invitations import router as invitations_router
from app.api.members import router as members_router
from app.api.middleware import CorrelationIDMiddleware
from app.api.users import router as users_router
from app.api.webhooks import router as webhooks_router
from app.api.websockets import router as websockets_router
from app.api.workspaces import router as workspaces_router
from app.core.config import settings
from app.core.logging import configure_logging

logger = structlog.get_logger()

app = FastAPI(
    title=settings.APP_NAME,
    description="Task Management API with GitHub Integration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class NoCacheMiddleware(BaseHTTPMiddleware):
    """Middleware to prevent browser caching of API responses."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        # Add headers to prevent caching
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


@app.on_event("startup")
async def startup_event() -> None:
    """Configure application on startup."""
    configure_logging()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging."""
    logger.error(
        "validation_error",
        path=request.url.path,
        errors=exc.errors(),
        body=await request.body(),
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# Add no-cache middleware (first)
app.add_middleware(NoCacheMiddleware)

# Add correlation ID middleware (before CORS)
app.add_middleware(CorrelationIDMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(workspaces_router)
app.include_router(boards_router)
app.include_router(cards_router)
app.include_router(invitations_router)
app.include_router(members_router)
app.include_router(webhooks_router)
app.include_router(websockets_router, tags=["websockets"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Taskly API", "status": "running"}
