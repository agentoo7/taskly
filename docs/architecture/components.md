# Components

## 1. API Layer (FastAPI Routes & Middleware)

**Responsibility:** HTTP request handling, validation, serialization, and routing.

**Key Interfaces:**
- `POST /auth/github/callback` - OAuth callback handler
- `POST /auth/refresh` - Refresh JWT access token
- `GET /workspaces` - List user's workspaces
- `POST /workspaces` - Create workspace
- `GET /boards/{id}` - Fetch board with cards
- `PATCH /cards/{id}` - Update card
- `POST /cards/bulk-update` - Batch card operations
- `POST /cards/{id}/create-branch` - Trigger branch creation
- `POST /webhooks/github` - GitHub webhook receiver
- `WebSocket /ws/boards/{board_id}` - Real-time board updates

**Dependencies:**
- Service Layer (business logic delegation)
- Authentication Middleware (JWT validation)
- WebSocket Manager (real-time broadcasts)

**Technology Stack:**
- FastAPI 0.109.0 with Pydantic 2.5.3 for request/response validation
- Uvicorn 0.27.0 ASGI server
- FastAPI dependency injection for service/repository wiring
- Middleware: CORS, rate limiting, request logging, error handling

## 2. Service Layer (Business Logic)

**Responsibility:** Orchestrates business operations, enforces business rules, coordinates between repositories and external services.

**Key Interfaces:**
- `WorkspaceService.create_workspace(name, creator_id) -> Workspace`
- `CardService.move_card(card_id, target_column_id, position) -> Card`
- `CardService.bulk_update(card_ids, updates) -> List[Card]`
- `GitIntegrationService.create_branch(card_id, repo_id, branch_name) -> Task`
- `WebhookService.process_pull_request_event(payload) -> None`
- `AuthService.exchange_github_code(code) -> Tuple[access_token, refresh_token]`

**Dependencies:**
- Repository Layer (data persistence)
- GitHub Client (external API calls)
- Celery Client (job enqueueing)
- WebSocket Manager (real-time notifications)
- Cache Manager (Redis operations)

## 3. Repository Layer (Data Access)

**Responsibility:** Abstract database operations, provide clean data access interface, handle query optimization.

**Key Interfaces:**
- `CardRepository.get_by_id(card_id) -> Optional[Card]`
- `CardRepository.get_by_board(board_id, filters) -> List[Card]`
- `CardRepository.update(card_id, updates) -> Card`
- `WorkspaceRepository.get_by_user(user_id) -> List[Workspace]`
- `PullRequestRepository.get_by_card(card_id) -> List[PullRequest]`
- `PullRequestRepository.upsert_from_github(pr_data) -> PullRequest`

**Dependencies:**
- SQLAlchemy Models (ORM layer)
- Database Session (async session management)

**Technology Stack:**
- SQLAlchemy 2.0.25 (async engine + async sessions)
- Repository pattern implementation (one repository per aggregate)

## 4. Background Workers (Celery Tasks)

**Responsibility:** Execute long-running, asynchronous operations without blocking API responses.

**Key Interfaces:**
- `create_branch_task(card_id, repo_id, branch_name, base_branch)`
- `process_webhook_task(event_type, payload, event_id)`
- `bulk_update_cards_task(card_ids, updates)`
- `send_invitation_email_task(email, workspace_name, token)`
- `sync_pull_request_task(pr_id)`

**Dependencies:**
- Service Layer (reuses business logic)
- Repository Layer (database updates)
- GitHub Client (API calls)
- WebSocket Manager (broadcast updates after task completion)

**Technology Stack:**
- Celery 5.3.4 with Redis 7.2.4 broker
- Task retry policies: exponential backoff (5s, 25s, 125s), max 3 retries
- Result backend: Redis

## 5. WebSocket Manager

**Responsibility:** Manage persistent WebSocket connections, broadcast real-time updates, handle reconnections.

**Key Interfaces:**
- `WebSocketManager.connect(websocket, board_id, user_id)`
- `WebSocketManager.disconnect(websocket)`
- `WebSocketManager.broadcast_to_board(board_id, message)`
- `WebSocketManager.send_to_user(user_id, message)`

**Dependencies:**
- Redis Pub/Sub (multi-instance coordination)
- FastAPI WebSocket support
- Authentication (validate JWT on connection)

**Technology Stack:**
- FastAPI native WebSocket
- Redis pub/sub for broadcasting across multiple Uvicorn instances
- Heartbeat mechanism (ping/pong every 30s)

## 6. GitHub Integration Service

**Responsibility:** Centralize all GitHub API interactions, handle rate limiting, implement retry logic.

**Key Interfaces:**
- `GitHubClient.create_branch(repo_full_name, branch_name, base_sha)`
- `GitHubClient.get_pull_request(repo_full_name, pr_number)`
- `GitHubClient.fetch_user_repos(access_token)`
- `GitHubClient.validate_webhook_signature(payload, signature, secret)`

**Dependencies:**
- httpx (async HTTP client)
- PyGithub (optional wrapper)
- Redis (rate limit caching, circuit breaker state)

**Technology Stack:**
- PyGithub 2.1.1 for high-level operations
- httpx 0.26.0 for custom requests
- Tenacity library for retry logic
- Circuit breaker pattern

## 7. Authentication & Authorization Module

**Responsibility:** Handle GitHub OAuth flow, JWT token generation/validation, permission checks.

**Key Interfaces:**
- `AuthService.authenticate_github(code) -> Tuple[User, access_token, refresh_token]`
- `AuthService.refresh_access_token(refresh_token) -> access_token`
- `AuthMiddleware.verify_token(token) -> User`
- `PermissionChecker.can_edit_board(user, board_id) -> bool`

**Dependencies:**
- User Repository
- GitHub Client (OAuth token exchange)
- Redis (token blacklist for logout)

**Technology Stack:**
- PyJWT 2.8.0 for JWT encoding/decoding
- GitHub OAuth 2.0 flow
- Access tokens: 15 min expiration, HS256 algorithm
- Refresh tokens: 7 day expiration

## 8. Shared Utilities

**Responsibility:** Cross-cutting concerns (logging, error handling, configuration).

**Key Interfaces:**
- `Logger.info(message, **context)`
- `ErrorHandler.handle_exception(exc, context) -> JSONResponse`
- `Config.get(key, default) -> Any`
- `CacheManager.get(key) -> Optional[Any]`
- `CacheManager.set(key, value, ttl) -> None`

**Dependencies:**
- structlog (structured logging)
- Redis (caching)
- Sentry SDK (error tracking)

**Technology Stack:**
- structlog 24.1.0 for JSON logging
- Redis for caching (5 min TTL for boards)
- Sentry 1.40.0 for exception capture
- Pydantic Settings for config management

---
