"""Redis cache configuration."""

from redis.asyncio import Redis

from app.core.config import settings

# Create Redis client
redis_client: Redis = Redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis() -> Redis:
    """Dependency for getting Redis client."""
    return redis_client
