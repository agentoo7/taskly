# Error Handling Strategy

## General Approach

- **Error Model:** RFC 7807 Problem Details
- **Exception Hierarchy:** Custom exceptions (ValidationError, UnauthorizedError, ForbiddenError, NotFoundError, etc.)
- **Error Propagation:** Repository → Service → API (enriched at each layer)
- **Global Handler:** FastAPI middleware catches all exceptions, sanitizes responses

## Logging Standards

- **Library:** structlog 24.1.0 (JSON logging)
- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Required Context:** correlation_id, user_id, service name, method name, duration
- **Sensitive Data Redaction:** Never log passwords, tokens, API keys, PII

## Error Handling Patterns

**External API Errors:**
- Retry policy: Exponential backoff (4s, 8s, 16s, 32s, 60s)
- Circuit breaker: After 5 failures, pause 60s
- Error translation: GitHub errors → domain exceptions

**Business Logic Errors:**
- Custom exceptions for domain rules
- User-facing error messages (clear, actionable)

**Data Consistency:**
- Transaction strategy: Atomic operations with rollback
- Idempotency: Webhook processing with deduplication
- Compensation logic: Reverse operations on failure

---
