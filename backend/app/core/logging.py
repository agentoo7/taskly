"""Structured logging configuration using structlog."""

import logging
import sys

import structlog


def configure_logging() -> None:
    """
    Configure structlog for JSON output with correlation IDs.

    This configuration:
    - Outputs JSON logs for production
    - Includes correlation IDs from context
    - Adds timestamps in ISO format
    - Includes logger name and log level
    - Formats exceptions with stack traces
    """
    structlog.configure(
        processors=[
            # Merge in context variables (correlation_id, etc.)
            structlog.contextvars.merge_contextvars,
            # Filter logs by level
            structlog.stdlib.filter_by_level,
            # Add timestamp in ISO format
            structlog.processors.TimeStamper(fmt="iso"),
            # Add logger name
            structlog.stdlib.add_logger_name,
            # Add log level
            structlog.stdlib.add_log_level,
            # Format positional args
            structlog.stdlib.PositionalArgumentsFormatter(),
            # Render stack info if present
            structlog.processors.StackInfoRenderer(),
            # Format exception info
            structlog.processors.format_exc_info,
            # Decode unicode
            structlog.processors.UnicodeDecoder(),
            # Final output as JSON
            structlog.processors.JSONRenderer(),
        ],
        # Use stdlib logging
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Cache logger instances
        cache_logger_on_first_use=True,
    )

    # Configure root logger
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
