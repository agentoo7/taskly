# Coding Standards

**⚠️ MANDATORY FOR AI AGENTS**

## Core Standards

- **Languages:** Python 3.11.7 with type hints (mandatory)
- **Type checking:** mypy strict mode
- **Formatter:** Black (line length: 100)
- **Linter:** Ruff
- **Async:** Always use async/await for I/O operations

## Critical Rules

1. **Never use synchronous database calls** (use `await`)
2. **All API responses must use Pydantic schemas** (not ORM models)
3. **Never log secrets or PII**
4. **All database operations must use repositories**
5. **Always set timeouts on external HTTP calls** (10s default)
6. **Celery tasks must be idempotent**
7. **Use correlation IDs in all log statements**
8. **Always validate UUIDs from URL paths**
9. **Database transactions must wrap multi-step operations**
10. **WebSocket broadcasts must include timestamp**

## Naming Conventions

- Files: snake_case (`card_service.py`)
- Classes: PascalCase (`CardService`)
- Functions: snake_case (`get_card_by_id()`)
- Constants: UPPER_SNAKE_CASE (`MAX_RETRY_ATTEMPTS`)
- Type hints: Always provide

---
