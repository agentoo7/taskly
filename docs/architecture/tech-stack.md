# Tech Stack

## Cloud Infrastructure

- **Provider:** DigitalOcean
- **Key Services:**
  - **Compute:** DigitalOcean Droplets (Docker containers) or App Platform (PaaS)
  - **Database:** Managed PostgreSQL 15
  - **Cache:** Managed Redis
  - **Load Balancer:** DigitalOcean Load Balancer
  - **Object Storage:** Spaces (S3-compatible, for file attachments if needed later)
  - **Secrets:** Environment variables via App Platform or Droplet env config
- **Deployment Regions:** Primary: `nyc3` (New York), Fallback: `sfo3` (San Francisco)

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| **Language** | Python | 3.11.7 | Backend development language | Type hints, async support, team familiarity, excellent FastAPI integration |
| **Runtime** | CPython | 3.11.7 | Python interpreter | Official implementation, best performance for FastAPI |
| **Package Manager** | UV | 0.1.18+ | Python dependency management | Extremely fast (10-100x faster than pip/poetry), reliable lock files, modern tool |
| **Web Framework** | FastAPI | 0.109.0 | REST API + WebSocket server | Async-native, automatic OpenAPI docs, Pydantic validation, WebSocket support |
| **ASGI Server** | Uvicorn | 0.27.0 | Production ASGI server | High performance, recommended for FastAPI, supports WebSockets |
| **Database** | PostgreSQL | 15.5 | Primary data store | JSONB flexibility, ACID transactions, full-text search, mature ORM support |
| **ORM** | SQLAlchemy | 2.0.25 | Database abstraction layer | Async support, flexible query builder, migration tools, type safety |
| **Migrations** | Alembic | 1.13.1 | Database schema versioning | Standard for SQLAlchemy, auto-generation, team workflows |
| **Cache/Broker** | Redis | 7.2.4 | Caching, Celery broker, pub/sub | Fast, supports multiple use cases, simple deployment |
| **Task Queue** | Celery | 5.3.4 | Background job processing | Mature, retry logic, monitoring tools (Flower), Redis integration |
| **Validation** | Pydantic | 2.5.3 | Data validation, serialization | Bundled with FastAPI, type-safe, excellent error messages |
| **Auth** | PyJWT | 2.8.0 | JWT token handling | Lightweight, standard JWT implementation |
| **HTTP Client** | httpx | 0.26.0 | Async HTTP (GitHub API calls) | Async-first, modern replacement for requests, timeout handling |
| **GitHub Integration** | PyGithub | 2.1.1 | GitHub API wrapper | Comprehensive API coverage, handles rate limits, type stubs available |
| **Testing Framework** | pytest | 7.4.4 | Unit and integration tests | Industry standard, async support (pytest-asyncio), extensive plugins |
| **Test Async** | pytest-asyncio | 0.23.3 | Async test support | Enables testing FastAPI async routes |
| **Test Coverage** | pytest-cov | 4.1.0 | Code coverage reporting | Integrates with pytest, generates reports for CI |
| **Linting** | Ruff | 0.1.14 | Fast Python linter | 10-100x faster than Flake8, replaces multiple tools |
| **Formatting** | Black | 24.1.1 | Code formatting | Opinionated, consistent style, team standard |
| **Type Checking** | mypy | 1.8.0 | Static type analysis | Catches type errors, enforces type hints, integrates with IDEs |
| **Logging** | structlog | 24.1.0 | Structured logging | JSON logs, contextual logging, correlation IDs, production-ready |
| **Monitoring** | Sentry SDK | 1.40.0 | Error tracking | Exception capture, performance monitoring, alerting |
| **Containerization** | Docker | 24.0.7 | Application packaging | Standard deployment, local dev parity, multi-stage builds |
| **Orchestration** | Docker Compose | 2.24.0 | Multi-container management | Local development, staging environments, simple orchestration |
| **CI/CD** | GitHub Actions | N/A | Automated testing/deployment | Native to GitHub, free for public repos, ecosystem integration |

---
