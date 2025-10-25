"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.middleware import CorrelationIDMiddleware
from app.api.users import router as users_router
from app.api.workspaces import router as workspaces_router
from app.core.config import settings
from app.core.logging import configure_logging

app = FastAPI(
    title=settings.APP_NAME,
    description="Task Management API with GitHub Integration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup_event() -> None:
    """Configure application on startup."""
    configure_logging()


# Add correlation ID middleware (before CORS)
app.add_middleware(CorrelationIDMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(workspaces_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Taskly API", "status": "running"}
