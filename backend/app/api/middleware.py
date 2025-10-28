"""API middleware for correlation tracking and request context."""

import time
import uuid
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add correlation ID to all requests.

    This middleware:
    - Generates or extracts correlation ID from X-Correlation-ID header
    - Binds correlation ID to structlog context for all logs in request
    - Adds correlation ID to response headers
    - Logs request start and completion with timing
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with correlation ID context.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response with correlation ID header
        """
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

        # Clear any existing context and bind new values
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            path=request.url.path,
            method=request.method,
        )

        # Log request start
        start_time = time.time()
        logger.info(
            "request.start",
            user_agent=request.headers.get("user-agent"),
        )

        # Process request
        try:
            response = await call_next(request)

            # Log request completion
            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "request.complete",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Add correlation ID to response
            response.headers["X-Correlation-ID"] = correlation_id
            return response

        except Exception as e:
            # Log request failure
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "request.failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2),
            )
            raise
