# Source Tree

```
backend/
├── alembic/                # Database migrations
├── app/
│   ├── api/               # API routes, middleware, dependencies
│   ├── services/          # Business logic
│   ├── repositories/      # Data access layer
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic request/response schemas
│   ├── tasks/             # Celery background tasks
│   ├── integrations/      # External service integrations (GitHub)
│   ├── websockets/        # WebSocket management
│   ├── core/              # Config, logging, database, cache, security
│   └── utils/             # Helper utilities
├── tests/
│   ├── unit/              # Unit tests (mocked dependencies)
│   ├── integration/       # Integration tests (real database)
│   └── fixtures/          # Test data factories
├── scripts/               # Utility scripts (seed data, reset DB)
├── .env.example           # Environment variable template
├── Dockerfile             # Production image
├── docker-compose.yml     # Local development
├── pyproject.toml         # UV dependency management (PEP 621)
├── uv.lock                # Locked dependencies (committed to git)
└── pytest.ini             # Pytest configuration
```

---
