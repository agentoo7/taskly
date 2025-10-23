# Epic 1: Foundation & Authentication

**Expanded Goal:** Establish the complete technical foundation for Taskly including development environment, CI/CD pipeline, database infrastructure, and GitHub OAuth authentication. This epic delivers a deployable application with working authentication flow, enabling users to sign in and access a basic landing page. By the end of this epic, the team has all infrastructure in place for rapid feature development with continuous deployment.

## Story 1.1: Project Setup & Development Environment

**As a** developer,
**I want** a fully configured monorepo development environment with Docker Compose,
**so that** I can run the entire application stack locally and start building features immediately.

### Acceptance Criteria

1. Monorepo structure created with `/frontend` (Next.js 14+) and `/backend` (FastAPI) directories
2. Docker Compose configuration orchestrates all services: Next.js dev server, FastAPI with hot reload, PostgreSQL 15+, Redis
3. All services start successfully with single `docker-compose up` command
4. Hot reload works for both frontend (Fast Refresh) and backend (--reload flag)
5. Frontend accessible at `http://localhost:3000`, backend API at `http://localhost:8000`
6. Health check endpoint (`GET /api/health`) returns 200 OK with service status
7. README documents setup instructions (prerequisites, running locally, stopping services)
8. Environment variables configured via `.env.example` template (no secrets committed)
9. TypeScript strict mode configured for frontend, mypy configured for backend
10. Linting configured (ESLint for frontend, Ruff/Black for backend) with pre-commit hooks

## Story 1.2: CI/CD Pipeline & Initial Deployment

**As a** developer,
**I want** an automated CI/CD pipeline that runs tests and deploys to staging,
**so that** we can ship changes confidently with every merge.

### Acceptance Criteria

1. GitHub Actions workflow triggers on every pull request and push to main branch
2. CI pipeline runs: linting (ESLint, Ruff), type checking (TypeScript, mypy), formatting validation (Prettier, Black)
3. Build verification step confirms Docker images build successfully for both frontend and backend
4. Pull requests blocked from merging if CI checks fail
5. Successful merges to main automatically deploy to staging environment
6. Staging environment accessible at designated URL (e.g., `https://staging.taskly.app` or cloud provider URL)
7. Deployment status visible in GitHub Actions UI with clear success/failure indicators
8. Rollback mechanism documented (can redeploy previous commit if deployment fails)
9. Environment secrets managed via GitHub Secrets or cloud provider secrets manager (not in repository)
10. Deployment logs accessible for debugging failed deployments

## Story 1.3: Database Foundation & Core Models

**As a** developer,
**I want** the foundational database schema and ORM models established,
**so that** I can build features on a solid, migrated data model.

### Acceptance Criteria

1. PostgreSQL 15+ running in Docker with persistent volume (data survives container restarts)
2. Alembic configured for database migrations with initial migration created
3. SQLAlchemy 2.0 (async) models defined for core entities: `users`, `workspaces`, `boards`, `cards`
4. `users` table includes: id (UUID), github_id (unique), username, email, avatar_url, created_at, updated_at
5. `workspaces` table includes: id (UUID), name, created_by (FK to users), created_at, updated_at
6. `boards` table includes: id (UUID), workspace_id (FK), name, columns (JSONB array), created_at, updated_at
7. `cards` table includes: id (UUID), board_id (FK), title, description (text), metadata (JSONB), column_id, position (integer), created_at, updated_at
8. Many-to-many relationship tables: `workspace_members` (user_id, workspace_id, role enum: admin/member)
9. Indexes created on all foreign keys for query performance
10. Migration applies successfully with `alembic upgrade head` and rolls back with `alembic downgrade -1`
11. Seed script (`scripts/seed_dev_data.py`) populates test data for local development

## Story 1.4: GitHub OAuth Authentication

**As a** user,
**I want** to sign in to Taskly using my GitHub account,
**so that** I can access the application without creating a new password.

### Acceptance Criteria

1. GitHub OAuth App registered with appropriate callback URL for local development and staging
2. Login page displays "Sign in with GitHub" button with GitHub branding (Octicon logo)
3. Clicking button initiates OAuth flow redirecting to GitHub authorization page
4. After user authorizes, GitHub redirects back to Taskly callback endpoint with authorization code
5. Backend exchanges authorization code for GitHub access token and stores encrypted in database
6. Backend fetches user profile from GitHub API (username, email, avatar) and creates/updates user record
7. Backend issues JWT access token (15 min expiration) and refresh token (7 day expiration) to frontend
8. Frontend stores tokens securely (httpOnly cookies or secure localStorage) and includes in subsequent API requests
9. Logout endpoint invalidates tokens and clears frontend storage
10. Unauthorized API requests (missing or expired token) return 401 status with clear error message
11. Token refresh mechanism automatically requests new access token using refresh token before expiration
12. GitHub API rate limits respected (cache user profile data, avoid excessive API calls)

## Story 1.5: User Landing Page & Navigation Shell

**As a** logged-in user,
**I want** to see a landing page with navigation structure,
**so that** I can understand the application layout and access future features.

### Acceptance Criteria

1. After successful login, user redirects to landing page (`/dashboard` or `/workspaces`)
2. Top navigation bar displays: Taskly logo, user avatar (from GitHub), username, logout button
3. Landing page shows "Welcome, [username]!" message confirming authentication worked
4. Navigation shell includes placeholder menu items: "Workspaces" (active), "Settings" (disabled/coming soon)
5. Clicking user avatar opens dropdown menu with: "Profile" (placeholder), "Settings" (placeholder), "Logout" (functional)
6. Logout button triggers logout endpoint, clears tokens, and redirects to login page
7. Responsive layout works on desktop (1280px+) and tablet (768px+) screen sizes
8. Dark mode toggle available in navigation (persists preference in localStorage, defaults to light mode)
9. Unauthenticated users accessing protected routes (`/dashboard`) automatically redirect to login page
10. Loading states display during authentication checks (prevent flash of incorrect content)
11. Error handling: if OAuth fails or GitHub API unreachable, display user-friendly error message with retry option

---
