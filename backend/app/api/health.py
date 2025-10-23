"""Health check endpoint for monitoring and Docker."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_redis
from app.core.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> dict[str, str | dict[str, str]]:
    """
    Health check endpoint that verifies all service connections.

    Returns:
        dict: Health status with service connection information
    """
    health_status: dict[str, str | dict[str, str]] = {
        "status": "healthy",
        "services": {},
    }
    services: dict[str, str] = {}

    # Check database connection
    try:
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        services["database"] = "connected"
    except Exception:
        services["database"] = "disconnected"
        health_status["status"] = "unhealthy"

    # Check Redis connection
    try:
        redis = await get_redis()
        await redis.ping()
        services["redis"] = "connected"
    except Exception:
        services["redis"] = "disconnected"
        health_status["status"] = "unhealthy"

    health_status["services"] = services
    return health_status
