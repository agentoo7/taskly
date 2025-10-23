# Technical Assumptions

## Repository Structure: Monorepo

**Decision:** Single repository containing both frontend (`/frontend`) and backend (`/backend`) directories.

**Rationale:**
- Enables atomic commits spanning both frontend and backend changes during rapid MVP development
- Simplifies CI/CD pipeline setup with single GitHub Actions workflow
- Easier coordination for small team (1-3 developers) without overhead of managing separate repos
- Reduces context switching between repositories during feature development
- Can split into polyrepo later if teams grow and need independent deployment cadence

**Tooling:** Use Turborepo or Nx for monorepo management (build caching, task orchestration) or keep simple with npm workspaces for MVP.

## Service Architecture

**Architecture Pattern:** Monolithic API (Single FastAPI Application) with Separate Job Queue

**Backend Service:**
- Single FastAPI application handling all REST endpoints and WebSocket connections
- Simpler to develop, debug, and deploy for MVP scale (<10k users)
- Scale vertically first (larger containers, more CPU/RAM) before considering microservices
- Avoid premature microservices complexity; monolith is appropriate until proven bottlenecks emerge

**Job Queue Architecture:**
- Separate Celery worker processes for long-running asynchronous tasks:
  - Git operations (branch creation, webhook processing)
  - Bulk actions (batch card updates, report generation)
  - Email notifications and background processing
- Redis as message broker and result backend
- Enables non-blocking API responses for Git operations while maintaining <3s user-facing latency

**WebSocket Service:**
- Integrated within FastAPI application for real-time board updates
- Maintains persistent connections for live collaboration and instant card sync
- Falls back to polling if WebSocket connection fails (graceful degradation)

**Deployment Pattern:** Docker Compose orchestrating multiple containers (Next.js, FastAPI, PostgreSQL, Redis, Celery worker) with single docker-compose.yml for development and production.

## Testing Requirements

**Testing Strategy:** Unit + Integration (Partial E2E Coverage)

**Unit Testing:**
- **Frontend:** Jest + React Testing Library for component tests, aim for 70%+ coverage on business logic
- **Backend:** pytest with pytest-asyncio for async FastAPI endpoints, aim for 80%+ coverage on API routes and business logic
- Focus on critical paths: Git integration, card CRUD operations, webhook handlers

**Integration Testing:**
- API integration tests using TestClient (FastAPI) to validate full request/response cycles
- Database integration tests with test database (PostgreSQL) to verify ORM queries and transactions
- GitHub API integration tests using mocked responses (vcr.py or responses library) to avoid rate limits

**E2E Testing (Limited Scope for MVP):**
- Playwright or Cypress for critical user flows only:
  - Onboarding: Signup → Connect GitHub → Create board → Link first card
  - Core workflow: Create card → Move to In Progress → Link PR → PR merge → Card auto-moves to Done
- Avoid comprehensive E2E coverage in MVP to maintain development velocity

**Manual Testing Conveniences:**
- Seed scripts for generating test workspaces, boards, and cards with realistic data
- Development mode with hot reload (Next.js Fast Refresh, FastAPI --reload)
- Docker Compose setup with easy reset (drop database, reseed) for clean testing environments

**CI/CD Testing Pipeline:**
- GitHub Actions workflow running on every PR:
  - Lint (ESLint, Ruff/Black for Python)
  - Type checking (TypeScript, mypy for Python)
  - Unit tests (frontend + backend)
  - Integration tests
  - Build verification (Docker image builds successfully)
- Block merges if tests fail or coverage drops below thresholds

## Additional Technical Assumptions and Requests

**Frontend Technology Stack:**
- **Framework:** Next.js 14+ with App Router (React Server Components for optimized performance)
- **Language:** TypeScript (strict mode) for type safety
- **UI Framework:** Tailwind CSS + shadcn/ui component library (accessible, customizable components based on Radix UI)
- **State Management:** Zustand or Jotai for client state, TanStack Query (React Query) for server state caching
- **Drag-and-Drop:** @dnd-kit library (modern, accessible, performant)
- **Timeline Rendering:** Custom implementation with D3.js or react-calendar-timeline
- **Real-Time Client:** Socket.IO client or native WebSocket API
- **Deployment:** Vercel (optimized for Next.js) or Docker containers on cloud platform

**Backend Technology Stack:**
- **Framework:** FastAPI (Python 3.11+) with async/await for high concurrency
- **Language:** Python 3.11+ with type hints (validated by mypy)
- **Database ORM:** SQLAlchemy 2.0 (async support) with Alembic for migrations
- **Authentication:** OAuth 2.0 for GitHub, JWT (PyJWT) for session management
- **GitHub Integration:** PyGithub or direct REST API calls using httpx (async HTTP client)
- **Background Tasks:** Celery + Redis for async job queue
- **Real-Time:** FastAPI WebSocket support or Socket.IO server
- **API Documentation:** Automatic OpenAPI docs via FastAPI (Swagger UI)

**Database:**
- **RDBMS:** PostgreSQL 15+
- **Why PostgreSQL:** JSONB for flexible card metadata, full-text search, strong consistency, excellent ORM support
- **Caching Layer:** Redis for session storage, frequently accessed boards, rate limiting, Celery message broker
- **Schema Design Principles:**
  - Core tables: workspaces, boards, cards, users, teams, git_repositories, pull_requests (cached GitHub data)
  - Many-to-many relationships: cards ↔ pull_requests (card can link multiple PRs), users ↔ workspaces
  - JSONB columns for flexible metadata (card labels, custom fields) without schema migrations
  - Indexes: B-tree on foreign keys, GIN indexes on JSONB for fast filtering

**Infrastructure & Hosting:**
- **Containerization:** Docker with multi-stage builds (optimized image sizes)
- **Local Development:** Docker Compose orchestrating all services (hot reload enabled)
- **Production Hosting:** Cloud platform (AWS, GCP, or DigitalOcean)
  - **Compute:** ECS (AWS), Cloud Run (GCP), or Droplets (DigitalOcean) running Docker containers
  - **Database:** Managed PostgreSQL (RDS, Cloud SQL, or DigitalOcean Managed Database)
  - **Cache:** Managed Redis (ElastiCache, Memorystore, or DigitalOcean Managed Redis)
  - **Load Balancer:** ALB (AWS) or cloud-native load balancer
- **CI/CD:** GitHub Actions for automated testing, Docker image building, deployment to staging/production
- **Secrets Management:** Environment variables via Docker secrets or cloud provider secrets manager (AWS Secrets Manager, GCP Secret Manager)

**Monitoring & Observability:**
- **Error Tracking:** Sentry for exception monitoring and alerting
- **Logging:** Structured JSON logs with correlation IDs for distributed tracing
- **Metrics:** Prometheus + Grafana or Datadog for application metrics (API latency, queue depth, Git operation success rates)
- **Uptime Monitoring:** UptimeRobot or Pingdom for external health checks

**Security:**
- **HTTPS Everywhere:** TLS 1.3 for all communications
- **Authentication:** GitHub OAuth (no password management), JWT with short expiration (15 min access, 7 day refresh)
- **Authorization:** Workspace-level RBAC (admin, member roles)
- **API Security:** Rate limiting (per-user, per-IP), CORS configuration, input validation (Pydantic models)
- **Data Encryption:** Encryption at rest for PostgreSQL, encrypted GitHub tokens in database
- **Secrets:** Never log tokens or secrets, rotate secrets regularly
- **Dependency Security:** Dependabot for automated vulnerability scanning, regular audits (npm audit, pip-audit)

**GitHub Integration Specifics:**
- **OAuth App:** For user authentication and basic repo access
- **GitHub App (Future):** For deeper permissions (webhooks, write access) in Phase 2; OAuth App sufficient for MVP
- **Webhook Handling:**
  - Idempotent handlers (handle duplicate webhook deliveries)
  - Signature verification (validate webhook authenticity)
  - Retry logic with exponential backoff for failed processing
  - Dead letter queue for persistently failing webhooks
- **Rate Limit Management:**
  - Aggressive caching of GitHub data (repos, PRs, commits)
  - Webhook-based updates instead of polling
  - Request batching where possible
  - Graceful degradation if rate limit exhausted (show stale data with warning)

**Performance Targets (Restated from NFRs):**
- Page load: <1s cached, <2s cold start
- View transitions: <500ms
- Git operations: <3s
- Real-time updates: <1s latency
- Support 100+ concurrent users per workspace

**Compliance & Data Governance:**
- **GDPR:** User data export (JSON format), right to deletion (cascade deletes), privacy policy
- **Data Retention:** Store Git event history (commits, PR updates) for 90 days by default, configurable per workspace
- **Audit Logs:** Track user actions for admin visibility (future enterprise feature)
- **SOC 2:** Deferred to enterprise tier post-MVP

---
