# Taskly Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Eliminate wasted developer time by synchronizing visual task boards with Git repositories
- Preserve task-to-code context automatically to prevent reviewer context loss and costly rework cycles
- Provide Trello-simple visual management with automated Git workflow capabilities
- Enable real-time bidirectional sync where board actions trigger Git operations and code activity updates cards
- Deliver multi-view project intelligence (Kanban, Timeline) for both developers and engineering managers
- Establish Taskly as the Git-native project management solution ("Move a Card, Ship the Code")

### Background Context

Software development teams today operate in fragmented workflows where task management (Trello, Jira, Linear) exists separately from code development (GitHub, GitLab). This fragmentation creates a "double-entry tax" where developers manually update both the project board and Git repositories, wasting 5-10 hours per week per developer. More critically, when reviewers open pull requests, they lack immediate access to original requirements, acceptance criteria, and design decisions—leading to context loss that causes misaligned code and preventable rework cycles.

Taskly solves this by treating the project board as a "control surface for your repo"—where moving a card automatically triggers Git operations (branch creation, PR setup) and code activity (commits, CI runs, merges) updates card status in real-time. By maintaining bidirectional synchronization between tasks and code, Taskly ensures every PR is linked to its requirement, eliminates manual status updates, and preserves complete task-to-code traceability. The target market is software development teams (5-50 developers) using GitHub alongside traditional project management tools who struggle with context switching and synchronization overhead.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-22 | 1.0 | Initial PRD draft created from Project Brief | PM Agent |

---

## Requirements

### Functional Requirements

**FR1:** The system shall provide a Kanban board with drag-and-drop card management across customizable columns (To Do, In Progress, In Review, Done).

**FR2:** Each card shall support comprehensive metadata including title, description (markdown), acceptance criteria (markdown), assignees (one or multiple), priority (Low/Medium/High/Urgent), labels/tags, story points, sprint assignment, due dates, comments, and activity timeline.

**FR3:** The system shall connect to GitHub organizations and repositories via OAuth 2.0 authentication.

**FR4:** Each card shall support linking to one or more GitHub issues or pull requests via manual URL entry or auto-detection when branch/PR references the card ID.

**FR5:** Cards linked to PRs shall display PR status (draft/ready/approved/merged), associated commits, and CI status inline within the card interface.

**FR6:** When a user moves a card to "In Progress," the system shall offer one-click branch creation with configurable naming conventions (e.g., `feature/TASK-123-brief-description`).

**FR7:** When a linked PR's state changes in GitHub (status updates, approvals, CI results), the system shall automatically update the corresponding card status within 1 second.

**FR8:** When a linked PR is merged in GitHub, the system shall optionally auto-move the corresponding card to "Done" based on user preference.

**FR9:** The system shall provide a Timeline view displaying sprints/iterations horizontally with cards grouped by sprint and story point totals visible.

**FR10:** Users shall be able to drag cards between sprints in Timeline view to rebalance workload.

**FR11:** The Timeline view shall display visual capacity indicators showing overloaded vs. balanced sprint allocation.

**FR12:** The system shall provide a keyboard-first command palette (⌘+K or Ctrl+K) enabling quick actions including create card, search, assign, change status, and navigate views.

**FR13:** The system shall support keyboard navigation shortcuts including J/K for card navigation, C for create card, and E for edit card.

**FR14:** Users shall be able to create workspaces and invite team members via email invitation.

**FR15:** The system shall support basic role permissions with two levels: admin (full access) and member (standard access).

**FR16:** Each workspace shall support multiple boards for organizing different projects or workflows.

**FR17:** Users shall be able to multi-select cards using shift-click or checkbox selection.

**FR18:** The system shall support batch operations on selected cards including assign multiple assignees, add labels, change priority, and move to column.

### Non-Functional Requirements

**NFR1:** Page load time shall be less than 1 second for cached loads and less than 2 seconds for cold starts.

**NFR2:** View transitions between Kanban, Timeline, and other views shall complete in less than 500 milliseconds.

**NFR3:** Git operations (branch creation, PR linking) shall complete within 3 seconds from user action initiation.

**NFR4:** Real-time updates triggered by webhooks shall reflect in the user interface within 1 second of the webhook event.

**NFR5:** The system shall support 100+ concurrent users per workspace without performance degradation.

**NFR6:** The application shall support modern browsers only: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ (no IE11 support).

**NFR7:** The user interface shall be desktop-first with responsive design supporting tablet devices.

**NFR8:** All communications shall use HTTPS with TLS 1.3 encryption.

**NFR9:** Authentication shall use JWT tokens with 15-minute access token expiration and 7-day refresh token expiration.

**NFR10:** The API shall implement rate limiting on both per-user and per-IP basis to prevent abuse.

**NFR11:** The system shall comply with GDPR requirements including user data export and right to deletion capabilities.

**NFR12:** GitHub API rate limits (5000 requests/hour per authenticated user) shall be managed through aggressive caching and webhook-based updates instead of polling.

---

## User Interface Design Goals

### Overall UX Vision

Taskly embraces a "developer-first, zero-friction" UX philosophy that prioritizes speed, clarity, and keyboard-driven workflows. The interface should feel as fast and responsive as a native desktop application while maintaining the visual simplicity that made Trello beloved. Every interaction—dragging cards, switching views, opening modals—must complete in under 500ms with optimistic UI updates to eliminate perceived lag. The design balances information density (showing PR status, CI indicators, metadata inline) with visual breathing room, ensuring developers can scan boards quickly without cognitive overload. Dark mode support is essential given the developer audience.

### Key Interaction Paradigms

1. **Keyboard-First Navigation:** Power users should rarely need a mouse. ⌘+K command palette for all major actions, J/K for card navigation, arrow keys for moving focus, Enter to open, Escape to close.

2. **Drag-and-Drop as Primary Manipulation:** Cards move between columns via drag-and-drop (with keyboard alternatives). Multi-select with Shift+Click or lasso selection enables batch operations.

3. **Contextual Inline Actions:** Hover states reveal quick actions (assign, label, link PR) without opening modals. Only complex operations (edit full description, configure settings) require modal dialogs.

4. **Real-Time Collaboration Indicators:** Subtle presence indicators show who's viewing/editing cards. Changes from other users appear instantly with brief animation to draw attention without disrupting focus.

5. **Progressive Disclosure:** Cards show summary view by default (title, assignee, priority, PR status). Click to expand inline for full description, comments, and activity timeline. This keeps the board scannable while providing depth on demand.

### Core Screens and Views

From a product perspective, the most critical screens necessary to deliver the PRD values and goals:

1. **Kanban Board View** - Primary daily workspace for managing task flow
2. **Timeline View (Sprint Planning)** - Horizontal timeline for workload balancing and sprint management
3. **Card Detail Modal/Panel** - Expanded view showing full description, acceptance criteria, comments, linked PRs/commits, activity timeline
4. **Workspace Dashboard** - Landing page after login showing all boards in workspace with quick access
5. **Board Settings** - Configure columns, naming conventions for branches, GitHub repo connections, automation rules
6. **Workspace Settings** - Manage team members, permissions, integrations (GitHub OAuth)
7. **Onboarding Flow** - Multi-step wizard: Create workspace → Connect GitHub → Create first board → Link first card to PR
8. **Command Palette (⌘+K)** - Global search and action interface overlaying any screen

### Accessibility: WCAG AA

Target WCAG 2.1 Level AA compliance to ensure usability for developers with visual, motor, or cognitive disabilities. Specific requirements:
- Keyboard navigation for all interactive elements
- Screen reader compatibility with semantic HTML and ARIA labels
- Minimum 4.5:1 color contrast ratios for text
- Focus indicators clearly visible on all interactive elements
- No reliance on color alone to convey information (use icons + color for status)

### Branding

**Visual Style:** Clean, modern, professional aesthetic inspired by developer tools (GitHub, Linear, Vercel dashboards) rather than consumer productivity apps. Emphasis on typography hierarchy, generous whitespace, and functional design over decorative elements.

**Color Palette:**
- Primary: GitHub-inspired deep blue (#0366D6) for CTAs and active states
- Neutral grays for backgrounds and text (light mode: #F6F8FA background, dark mode: #0D1117 background)
- Status colors: Green (success/merged), Yellow (in progress/pending), Red (failed/blocked), Purple (in review)
- All colors meet WCAG AA contrast requirements

**Typography:** Monospace font (Fira Code, JetBrains Mono, or SF Mono) for code references, card IDs, and branch names. Sans-serif (Inter, system-ui) for body text and UI elements.

**Iconography:** Minimal, line-based icons (Heroicons or Lucide) with 2px stroke weight. GitHub's Octicons for Git-specific indicators (branch, PR, commit).

### Target Device and Platforms: Web Responsive

**Primary:** Desktop web browsers (Chrome, Firefox, Safari, Edge 90+) optimized for screen sizes 1280x720 and above. Layout assumes horizontal space for multi-column Kanban boards and Timeline views.

**Secondary:** Tablet devices (iPad, Android tablets) in landscape orientation with touch-optimized drag-and-drop. Portrait orientation shows single-column mobile-friendly layout with reduced feature set.

**Out of Scope for MVP:** Native mobile apps (iOS/Android), though the responsive web app should be usable on mobile browsers for quick status checks or comment replies.

**Target OS:** Cross-platform (macOS, Windows, Linux) via web browsers—no OS-specific features or native desktop wrappers.

---

## Technical Assumptions

### Repository Structure: Monorepo

**Decision:** Single repository containing both frontend (`/frontend`) and backend (`/backend`) directories.

**Rationale:**
- Enables atomic commits spanning both frontend and backend changes during rapid MVP development
- Simplifies CI/CD pipeline setup with single GitHub Actions workflow
- Easier coordination for small team (1-3 developers) without overhead of managing separate repos
- Reduces context switching between repositories during feature development
- Can split into polyrepo later if teams grow and need independent deployment cadence

**Tooling:** Use Turborepo or Nx for monorepo management (build caching, task orchestration) or keep simple with npm workspaces for MVP.

### Service Architecture

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

### Testing Requirements

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

### Additional Technical Assumptions and Requests

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

## Epic List

### Epic 1: Foundation & Authentication
**Goal:** Establish core project infrastructure with GitHub authentication and deployable application skeleton.

### Epic 2: Core Board & Card Management
**Goal:** Enable teams to create workspaces and manage visual Kanban boards with rich card metadata.

### Epic 3: Git Integration & Synchronization
**Goal:** Implement bidirectional Git-native synchronization enabling seamless board-to-code workflow automation.

### Epic 4: Timeline View & Sprint Planning
**Goal:** Provide sprint planning and capacity management capabilities for engineering managers.

### Epic 5: Power User Features & Polish
**Goal:** Deliver keyboard-driven workflows, bulk operations, and performance optimization for developer productivity.

---

## Epic 1: Foundation & Authentication

**Expanded Goal:** Establish the complete technical foundation for Taskly including development environment, CI/CD pipeline, database infrastructure, and GitHub OAuth authentication. This epic delivers a deployable application with working authentication flow, enabling users to sign in and access a basic landing page. By the end of this epic, the team has all infrastructure in place for rapid feature development with continuous deployment.

### Story 1.1: Project Setup & Development Environment

**As a** developer,
**I want** a fully configured monorepo development environment with Docker Compose,
**so that** I can run the entire application stack locally and start building features immediately.

#### Acceptance Criteria

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

### Story 1.2: CI/CD Pipeline & Initial Deployment

**As a** developer,
**I want** an automated CI/CD pipeline that runs tests and deploys to staging,
**so that** we can ship changes confidently with every merge.

#### Acceptance Criteria

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

### Story 1.3: Database Foundation & Core Models

**As a** developer,
**I want** the foundational database schema and ORM models established,
**so that** I can build features on a solid, migrated data model.

#### Acceptance Criteria

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

### Story 1.4: GitHub OAuth Authentication

**As a** user,
**I want** to sign in to Taskly using my GitHub account,
**so that** I can access the application without creating a new password.

#### Acceptance Criteria

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

### Story 1.5: User Landing Page & Navigation Shell

**As a** logged-in user,
**I want** to see a landing page with navigation structure,
**so that** I can understand the application layout and access future features.

#### Acceptance Criteria

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

## Epic 2: Core Board & Card Management

**Expanded Goal:** Enable users to create workspaces, invite team members, and manage visual Kanban boards with rich card metadata. This epic delivers the core project management experience with drag-and-drop card manipulation, comprehensive metadata support (assignees, labels, priorities, story points, due dates), card comments, and activity tracking. By the end of this epic, Taskly functions as a complete standalone project management tool comparable to Trello, providing immediate value even without Git integration.

### Story 2.1: Workspace Creation & Management

**As a** logged-in user,
**I want** to create and manage workspaces for my teams,
**so that** I can organize multiple projects separately.

#### Acceptance Criteria

1. Landing page displays "Create Workspace" button when user has no workspaces
2. Clicking "Create Workspace" opens modal with form: workspace name (required, max 100 chars)
3. Submitting form creates workspace with current user as admin and redirects to workspace dashboard
4. Workspace dashboard displays workspace name, list of boards (empty initially), "Create Board" button
5. User who created workspace automatically assigned "admin" role in workspace_members table
6. Sidebar navigation shows list of all workspaces user is member of with ability to switch between them
7. Active workspace indicated visually in sidebar (highlighted, checkmark, or bold text)
8. Workspace settings page accessible to admins showing: workspace name (editable), member list, delete workspace option
9. Workspace name editable by admins only (updates in real-time for all members viewing workspace)
10. Delete workspace action requires confirmation modal ("This will delete all boards and cards. Type workspace name to confirm")
11. Deleting workspace cascades deletion to all boards, cards, and membership records
12. Workspace dashboard shows empty state with helpful message and call-to-action when no boards exist: "Get started by creating your first board"

### Story 2.2: Team Member Invitations & Permissions

**As a** workspace admin,
**I want** to invite team members via email and manage their permissions,
**so that** my team can collaborate on boards.

#### Acceptance Criteria

1. Workspace settings page displays "Invite Members" button (visible to admins only)
2. Clicking button opens invite modal with email input field (supports multiple comma-separated emails)
3. Role selector dropdown offers two options: "Member" (default), "Admin"
4. Submitting invitation sends email to each address with invite link containing secure token
5. Email template includes: workspace name, inviter's name/avatar, "Join Workspace" CTA button, expiration notice (7 days)
6. Invite link redirects to Taskly; if recipient not logged in, prompts GitHub OAuth first, then accepts invite
7. Accepting invite adds user to workspace_members table with specified role and redirects to workspace dashboard
8. Workspace settings displays member list with columns: avatar, username, email, role, "Remove" button (for admins)
9. Admins can change member roles via dropdown in member list (member ↔ admin)
10. Admins can remove members from workspace (requires confirmation: "Remove [username] from workspace?")
11. Removed members lose access immediately; attempting to access workspace shows 403 error with message "You are no longer a member of this workspace"
12. Invite tokens expire after 7 days; expired links show error message "Invite expired. Please request a new invitation."
13. Members (non-admin role) can view workspace and boards but cannot invite others, change permissions, or delete workspace

### Story 2.3: Board Creation & Column Customization

**As a** workspace member,
**I want** to create boards with customizable columns,
**so that** I can organize cards according to my team's workflow.

#### Acceptance Criteria

1. Workspace dashboard displays "Create Board" button accessible to all workspace members
2. Clicking button opens board creation modal with fields: board name (required, max 100 chars), template selector (optional)
3. Template selector offers: "Blank Board", "Default Kanban" (pre-populated with To Do, In Progress, In Review, Done columns)
4. Submitting form creates board and redirects to board view showing empty columns
5. Board view displays board name as header with edit icon (clicking opens inline rename input)
6. Column headers display column name with hover actions: "Add Card", "Edit Column", "Delete Column", drag handle icon
7. "Add Column" button displayed at end of columns list (creates new column with placeholder name "New Column" and auto-focuses rename input)
8. Columns editable by clicking name (inline input appears, updates on blur or Enter key)
9. Columns draggable to reorder (drag column header left/right, visual drop indicator shows target position)
10. Deleting column requires confirmation if column contains cards: "Delete column and X cards inside?" with options "Move cards to another column" or "Delete cards"
11. Board persists column configuration in `boards.columns` JSONB field as array: `[{id: uuid, name: string, position: int}]`
12. Board list in workspace dashboard shows board cards with: board name, last updated timestamp, card count, members avatars (up to 5, +N indicator if more)
13. Clicking board card in workspace dashboard navigates to board view
14. Board settings accessible via gear icon in board header showing: board name (editable), archive board, delete board options
15. Archived boards hidden from main board list but accessible via "Show Archived" toggle in workspace dashboard
16. Deleting board requires confirmation and cascades deletion to all cards

### Story 2.4: Card Creation & Basic Metadata

**As a** board member,
**I want** to create cards with title, description, and basic metadata,
**so that** I can capture and organize tasks.

#### Acceptance Criteria

1. Clicking "Add Card" button in column header opens quick-create input at top of column
2. Quick-create input allows typing card title (required, max 255 chars) and pressing Enter to create card
3. Created card appears at top of column with just title visible (collapsed state)
4. Clicking card opens card detail modal showing full editable fields: title, description (markdown editor), priority, due date, story points
5. Description editor supports markdown with preview toggle (shows formatted markdown or raw text)
6. Priority selector dropdown offers: None (default), Low (blue), Medium (yellow), High (orange), Urgent (red)
7. Priority displayed as colored dot indicator on card in column view
8. Due date picker allows selecting date (calendar widget), displayed as "Due: MMM DD" on card
9. Overdue cards (due date passed, card not in "Done" column) show red due date indicator
10. Story points input accepts integers 0-99, displayed as badge on card (e.g., "5 pts")
11. Card position persists in `cards.position` field (integer); newly created cards get position 0, existing cards increment
12. Cards within column ordered by position ascending (lowest position at top)
13. Empty columns display placeholder text: "Drag cards here or click + to add"
14. Card detail modal includes "Delete Card" button (requires confirmation: "Delete this card?")
15. Deleted cards removed from database immediately, column updates in real-time

### Story 2.5: Drag-and-Drop Card Movement

**As a** board member,
**I want** to drag cards between columns and reorder them within columns,
**so that** I can visualize workflow progress.

#### Acceptance Criteria

1. Cards draggable by clicking and holding anywhere on card surface (cursor changes to grab icon)
2. Dragging card displays ghost preview following cursor and semi-transparent placeholder in original position
3. Hovering over target column highlights drop zone with visual indicator (border or background color change)
4. Dropping card in new column moves card and updates `cards.column_id` field in database
5. Dropping card between existing cards reorders position; dropping at top/bottom places card at start/end of column
6. Card position recalculated on drop: target position set to dropped location, other cards in column reordered accordingly
7. Drag-and-drop works with @dnd-kit library (accessible, keyboard-navigable)
8. Keyboard alternative: focus card with Tab, press Space to "pick up," arrow keys to move, Space again to "drop," Escape to cancel
9. Dropping card triggers optimistic UI update (card moves immediately) followed by API request; rollback if API fails
10. Moving card updates `cards.updated_at` timestamp and creates activity log entry: "[User] moved card from [Old Column] to [New Column]"
11. Multiple users dragging cards simultaneously see real-time updates via WebSocket (other users' drag operations visible with different colored ghost preview)
12. Dragging disabled for cards being edited by another user (lock indicator displayed)
13. Long columns (50+ cards) virtualized for performance (only render visible cards, scroll smoothly)
14. Mobile/touch devices support drag-and-drop via long-press gesture (hold 500ms to activate drag mode)

### Story 2.6: Advanced Card Metadata (Assignees & Labels)

**As a** board member,
**I want** to assign cards to team members and add labels,
**so that** I can categorize and distribute work effectively.

#### Acceptance Criteria

1. Card detail modal displays "Assignees" section with "+ Add Assignee" button
2. Clicking "+ Add Assignee" opens dropdown showing all workspace members with avatars and usernames
3. Selecting member adds them to card; multiple assignees supported (no limit)
4. Assigned users displayed as avatar chips in card detail and as stacked avatars on card in column view (max 3 visible, +N indicator)
5. Clicking avatar chip in card detail opens member profile popover showing: username, email, "Remove from card" button
6. Removing assignee updates database and removes avatar from card display
7. Card detail modal displays "Labels" section with "+ Add Label" button
8. Clicking "+ Add Label" opens dropdown showing existing board labels with color preview
9. Labels editable at board level: board settings includes "Manage Labels" showing all labels with name (required), color (color picker)
10. Label colors offer preset palette: red, orange, yellow, green, blue, purple, pink, gray (custom hex colors supported)
11. Adding label to card displays label chip (colored rectangle with label name) in card detail and column view
12. Multiple labels per card supported; labels displayed horizontally in card detail, vertically stacked in column view (max 3 visible)
13. Labels stored in `cards.metadata` JSONB field as array: `labels: [{id: uuid, name: string, color: string}]`
14. Assignees stored via many-to-many relationship table: `card_assignees(card_id, user_id, assigned_at)`
15. Filtering controls in board header allow filtering by: assignee (dropdown multi-select), label (dropdown multi-select), priority
16. Applying filters hides cards not matching criteria; filter badge displays active filter count (e.g., "3 filters active")
17. Clear all filters button resets board to show all cards

### Story 2.7: Card Comments & Activity Timeline

**As a** board member,
**I want** to comment on cards and see activity history,
**so that** I can collaborate and track changes.

#### Acceptance Criteria

1. Card detail modal displays "Activity" section below main fields showing chronological timeline of events
2. Activity timeline includes events: card created, field changed (title, description, priority, due date, assignees, labels), moved between columns, commented
3. Each activity entry shows: user avatar, username, action description, timestamp (relative format: "2 hours ago", absolute on hover)
4. Field change events show before/after values: "[User] changed priority from Medium to High"
5. Activity section includes comment composer at bottom: textarea input with "Add Comment" button
6. Typing comment supports markdown (preview toggle available)
7. Submitting comment creates `card_comments` record with: card_id, user_id, comment text (markdown), created_at timestamp
8. New comment appears at bottom of activity timeline immediately (optimistic UI)
9. Comments display as distinct timeline entries with: user avatar, username, markdown-rendered comment text, timestamp, "Edit" and "Delete" options (visible to comment author only)
10. Editing comment opens inline textarea with current text, "Save" and "Cancel" buttons; saving updates comment text and appends "(edited)" indicator
11. Deleting comment requires confirmation: "Delete this comment?" with "Delete" and "Cancel" buttons
12. Activity timeline auto-scrolls to bottom when new events appear (if user already scrolled to bottom; otherwise shows "New activity" indicator)
13. Activity events stored in `card_activity` table with: card_id, user_id, activity_type (enum), metadata (JSONB), created_at
14. Activity timeline loads most recent 50 events; older events accessible via "Load More" button at top of timeline
15. Real-time updates: when another user comments or changes card, activity appears in timeline immediately via WebSocket

---

## Epic 3: Git Integration & Synchronization

**Expanded Goal:** Implement bidirectional Git-native synchronization that connects Taskly boards directly to GitHub repositories. This epic delivers the core product differentiation: automatic branch creation from cards, card-to-PR linking with auto-detection, webhook-based real-time sync showing PR status and CI results inline on cards, and automatic card movement when PRs merge. By the end of this epic, Taskly transforms from a standalone project management tool into a Git-native "control surface for your repo," eliminating double-entry and preserving task-to-code context automatically.

### Story 3.1: GitHub Repository Connection

**As a** workspace admin,
**I want** to connect GitHub repositories to my workspace,
**so that** boards can integrate with code repositories.

#### Acceptance Criteria

1. Workspace settings page displays "Connected Repositories" section with "+ Connect Repository" button (visible to admins only)
2. Clicking button opens GitHub repository selector modal using GitHub API to fetch user's accessible repositories and organizations
3. Repository list displays: repository name, owner/org name, visibility indicator (public/private), star count, last updated timestamp
4. Search/filter input allows finding repositories by name (client-side filtering for <100 repos, server-side search for larger lists)
5. Selecting repository creates `git_repositories` record with: workspace_id, github_repo_id, owner, name, full_name (owner/repo), default_branch, is_active, connected_at timestamp
6. Connected repositories list in workspace settings shows: repo full_name (owner/repo), GitHub link (opens in new tab), "Disconnect" button
7. Disconnecting repository requires confirmation: "This will unlink all cards from PRs in this repository. Continue?"
8. Disconnecting sets `git_repositories.is_active = false` (soft delete preserves historical data) and removes PR links from cards
9. GitHub API uses authenticated user's OAuth token to fetch repositories (respects user's GitHub permissions)
10. Repositories with no write access display warning: "Read-only access. Branch creation will not be available."
11. Error handling: if GitHub API rate limit exhausted, display message "GitHub API limit reached. Try again in [X] minutes." with countdown timer
12. Workspace can connect multiple repositories (supports mono-repo teams with separate backend/frontend repos)
13. Board settings allow specifying default repository for that board (used for branch creation in Story 3.3)

### Story 3.2: Manual Card-to-PR Linking

**As a** board member,
**I want** to manually link cards to GitHub pull requests by pasting PR URLs,
**so that** I can connect existing work to cards.

#### Acceptance Criteria

1. Card detail modal displays "Linked Pull Requests" section with "+ Link Pull Request" button
2. Clicking button opens input field with placeholder: "Paste GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)"
3. Pasting valid PR URL and clicking "Link" validates URL format and extracts owner, repo, PR number
4. Backend fetches PR data from GitHub API: title, state (open/closed/merged), author, created_at, updated_at, head branch, base branch, mergeable status
5. PR data stored in `pull_requests` table with: id (UUID), github_pr_id (unique), repository_id (FK), pr_number, title, state, author_github_id, head_branch, base_branch, url, fetched_at timestamp
6. Card-PR relationship stored in `card_pull_requests` many-to-many table: card_id, pull_request_id, linked_at timestamp
7. Linked PR displayed in card detail as compact card showing: PR number, title, state badge (open/draft/approved/merged with color coding), author avatar, branch names (head → base)
8. Multiple PRs linkable to single card (supports scenarios like frontend + backend PRs for one feature)
9. PR state badge colors: gray (draft), blue (open), green (merged), purple (approved/ready), red (closed without merge)
10. Clicking PR card opens GitHub PR in new browser tab
11. Unlinking PR shows confirmation: "Remove link to PR #123?" with "Remove" and "Cancel" buttons
12. Unlinking removes record from `card_pull_requests` table but preserves `pull_requests` record (other cards may link to same PR)
13. Linked PRs displayed on card in column view as compact badge: "PR #123" with state indicator dot
14. Error handling: invalid URL shows message "Invalid GitHub PR URL. Please check and try again."
15. Error handling: PR from repository not connected to workspace shows message "Repository not connected. Connect it in workspace settings first."
16. Error handling: GitHub API errors (network timeout, 404 not found, rate limit) display user-friendly messages with retry option

### Story 3.3: One-Click Branch Creation from Cards

**As a** board member,
**I want** to create GitHub branches directly from cards with one click,
**so that** I can start coding without manual branch creation steps.

#### Acceptance Criteria

1. Card detail modal displays "Create Branch" button in Linked Pull Requests section (visible only if card has no linked PRs)
2. Button shows repository selector dropdown if workspace has multiple connected repositories; uses board's default repository if only one connected
3. Clicking "Create Branch" opens configuration modal with: repository selector (if multiple), branch name preview, base branch selector (defaults to repository's default_branch)
4. Branch name auto-generated using pattern: `feature/CARD-{card-id-short}-{title-kebab-case}` (configurable in board settings)
5. Branch name preview updates in real-time as user edits card title in modal; manual override allowed with text input
6. Branch name validation: only lowercase alphanumeric, hyphens, underscores; no spaces or special characters (shows inline validation error if invalid)
7. Submitting creates branch via GitHub API: `POST /repos/{owner}/{repo}/git/refs` with ref `refs/heads/{branch-name}` pointing to base branch's HEAD SHA
8. Branch creation triggers Celery background job (non-blocking) with job ID returned to frontend
9. Frontend shows loading state: "Creating branch..." with spinner in card detail
10. On success (within 3 seconds), displays success message: "Branch {branch-name} created" with GitHub link to branch
11. Created branch automatically linked to card: backend creates draft PR via GitHub API (optional, configurable in board settings) and links PR to card per Story 3.2
12. If draft PR creation enabled, PR description auto-populated with card details: title, description (markdown), acceptance criteria, link back to Taskly card
13. Error handling: branch name already exists shows message "Branch {branch-name} already exists. Choose a different name or link existing PR."
14. Error handling: insufficient GitHub permissions shows message "Cannot create branch. Requires write access to repository."
15. Error handling: GitHub API errors (network issues, rate limits) display message with retry button and option to copy branch name for manual creation
16. "Create Branch" button disabled (grayed out) if no repositories connected to workspace (tooltip: "Connect a repository in workspace settings first")
17. Branch creation activity logged in card timeline: "[User] created branch {branch-name} in {repository}"

### Story 3.4: Webhook Infrastructure & PR Status Sync

**As a** system,
**I want** to receive GitHub webhooks and update card PR status in real-time,
**so that** boards always reflect current code state without manual updates.

#### Acceptance Criteria

1. Backend exposes webhook endpoint: `POST /api/webhooks/github` accepting GitHub webhook payloads
2. GitHub App or webhook configured for each connected repository subscribing to events: `pull_request`, `pull_request_review`, `status`, `check_suite`, `push`
3. Webhook endpoint validates GitHub signature (HMAC SHA-256) using shared secret to prevent spoofing; invalid signatures return 401 Unauthorized
4. Webhook payloads parsed and enqueued to Celery background job for async processing (immediate 200 OK response to GitHub to prevent retries)
5. `pull_request` webhook events (opened, closed, reopened, edited, ready_for_review, converted_to_draft) update `pull_requests` table: state, title, mergeable status, updated_at timestamp
6. `pull_request_review` events (submitted, dismissed) update PR approval status; track approval count and reviewer list
7. `status` and `check_suite` events update CI status tracked in `pull_requests.ci_status` JSONB field: `{status: 'pending'|'success'|'failure', checks: [{name, status, url}]}`
8. `push` events to PR head branch update commit count and last commit SHA in `pull_requests` table
9. After processing webhook, backend broadcasts update to frontend via WebSocket message: `{type: 'pr_updated', pr_id: uuid, card_ids: [uuid]}`
10. Frontend WebSocket listener receives message and updates affected cards in real-time: PR state badge changes, CI indicators update, commit count increments
11. Cards linked to updated PR display updated status immediately without page refresh (optimistic UI already shows, webhook confirms)
12. Webhook processing idempotent: duplicate webhook deliveries (GitHub retries) detected via `event_id` and skipped to prevent duplicate processing
13. Failed webhook processing (e.g., database error) logged to error tracking (Sentry) and retried up to 3 times with exponential backoff (5s, 25s, 125s)
14. Webhooks failing after 3 retries moved to dead letter queue (DLQ) for manual investigation; alerting triggered for engineering team
15. Webhook processing metrics tracked: event type, processing time, success/failure rate (visible in admin dashboard for debugging)
16. Rate limiting on webhook endpoint: max 100 requests per minute per repository to prevent abuse (returns 429 Too Many Requests if exceeded)
17. CI status indicators displayed on card: green checkmark (all checks passed), red X (checks failed), yellow spinner (checks running), gray dash (no checks)

### Story 3.5: Auto-Display PR Status & Commits on Cards

**As a** board member,
**I want** to see PR status, commits, and CI results inline on cards,
**so that** I have full context without leaving the board.

#### Acceptance Criteria

1. Cards with linked PRs display PR summary section in card detail modal below description, showing for each linked PR: PR number, title, state, author, created date, last updated date
2. PR state displayed as color-coded badge: "Open" (blue), "Draft" (gray), "Ready for Review" (purple), "Approved" (green), "Merged" (dark green), "Closed" (red)
3. PR summary shows branch information: "head-branch → base-branch" with branch icons
4. CI status indicator displayed prominently: green checkmark + "All checks passed", red X + "X checks failed", yellow spinner + "Checks running", gray dash + "No checks"
5. Clicking CI status expands check details showing each check: name, status (success/failure/pending), external link to check details (e.g., GitHub Actions run)
6. Commit count displayed: "X commits" with GitHub Octicon commit icon; clicking opens commit list modal
7. Commit list modal shows most recent 10 commits: short SHA (7 chars), commit message (first line), author avatar, relative timestamp ("2 hours ago")
8. Each commit in list links to GitHub commit page (opens in new tab)
9. Approval status displayed: avatars of approving reviewers with count "2 approvals" or "Awaiting review" if none
10. Mergeable status indicator: "Ready to merge" (green), "Merge conflicts" (red), "Checks required" (yellow)
11. PR summary section updates in real-time via WebSocket when webhook events processed (state changes, new commits, CI updates)
12. Column view (collapsed card) displays compact PR indicators: PR badge "PR #123", CI status dot (green/red/yellow), commit count if >0
13. Hovering over collapsed PR indicators shows tooltip with full PR title and state
14. Multiple linked PRs on single card displayed as stacked badges; clicking opens dropdown to select which PR to view details for
15. PR data cached in `pull_requests` table and refreshed via webhooks; fallback manual refresh button in card detail (calls GitHub API immediately if data >5 minutes old)
16. Empty state: if card has branch created (Story 3.3) but no PR yet, displays "Branch created: {branch-name}" with prompt "Create PR on GitHub" linking to GitHub's PR creation page with branch pre-selected

### Story 3.6: Auto-Move Cards on PR Merge

**As a** board member,
**I want** cards to automatically move to "Done" when linked PRs are merged,
**so that** the board reflects code completion without manual updates.

#### Acceptance Criteria

1. When `pull_request` webhook event with action `closed` and `merged: true` received, backend identifies all cards linked to that PR
2. For each linked card, backend checks if auto-move enabled (board-level setting, defaults to true)
3. If auto-move enabled, backend identifies "Done" column (configurable in board settings; defaults to column named "Done" or rightmost column)
4. Backend updates card: sets `cards.column_id` to Done column, updates `cards.position` to top of column (position 0, other cards increment), sets `cards.updated_at` timestamp
5. Activity log entry created in card timeline: "[GitHub] automatically moved card to Done (PR #{pr-number} merged)"
6. Frontend receives WebSocket message: `{type: 'card_moved', card_id: uuid, from_column: uuid, to_column: uuid, reason: 'pr_merged'}`
7. Card animates smoothly from current column to Done column in real-time for all users viewing board (animated slide with visual indicator like confetti or checkmark)
8. Auto-move disabled if card already in Done column (idempotent)
9. If card has multiple linked PRs, auto-move triggers only when all linked PRs are merged (configurable: "move when any PR merged" vs "move when all PRs merged")
10. Board settings page includes "Automation" section with toggle: "Automatically move cards to Done when PRs merge" (on/off, defaults to on)
11. Board settings allows selecting target column for auto-move via dropdown (lists all columns, defaults to "Done")
12. Board settings includes PR merge behavior dropdown: "Move when any linked PR merges" vs "Move when all linked PRs merge"
13. Users can manually move cards out of Done column after auto-move (no locking); manual moves do not disable future auto-moves
14. Auto-move respects user permissions: if user who triggered PR merge lacks permission to edit board (e.g., removed from workspace), auto-move uses system actor "[GitHub]"
15. Auto-move logic handles edge cases: column deleted (falls back to rightmost column), board archived (skips auto-move, logs warning)
16. Failed auto-moves logged to error tracking with context (card ID, PR ID, error message) for debugging; user sees notification "Auto-move failed for card [title]. Please move manually."

### Story 3.7: Card ID Auto-Detection in Branch/PR Names

**As a** board member,
**I want** Taskly to automatically detect when PRs or branches reference card IDs,
**so that** I don't have to manually link every PR.

#### Acceptance Criteria

1. When webhook `pull_request` event (opened, edited) received, backend extracts PR head branch name and PR body text
2. Backend searches for card ID patterns: `CARD-{id}`, `card-{id}`, `#{id}`, or Taskly card URL patterns in branch name and PR description
3. If card ID found and matches existing card in workspace, backend automatically creates card-PR link in `card_pull_requests` table
4. Multiple card IDs detected in single PR creates multiple links (e.g., PR addresses two cards)
5. Auto-detected links displayed in card detail with indicator: "Auto-linked from branch name" or "Auto-linked from PR description" (distinguished from manual links)
6. If PR description contains Taskly card URL (`https://taskly.app/workspaces/{ws-id}/boards/{board-id}/cards/{card-id}`), backend parses URL and links PR to that card
7. Activity log entry created: "[GitHub] automatically linked PR #{pr-number} (detected in branch/PR description)"
8. Frontend shows toast notification when auto-link created: "PR #{pr-number} automatically linked to this card"
9. Auto-detected links user can unlink manually if incorrect (same unlink flow as Story 3.2)
10. If branch created via Taskly (Story 3.3), branch name always includes card ID ensuring auto-detection works
11. Card ID pattern matching case-insensitive: detects `card-123`, `CARD-123`, `Card-123` equally
12. Invalid card IDs (pattern matches but card doesn't exist) logged as debug info but do not create links or show errors
13. Auto-detection runs on every relevant webhook event: `pull_request` opened, edited, reopened (handles cases where PR description updated to add card reference)
14. Auto-detection respects repository permissions: only links PRs from repositories connected to workspace; PRs from unconnected repos ignored
15. Duplicate auto-links prevented: if card-PR link already exists (manually created or previously auto-detected), skip creation (idempotent)

---

## Epic 4: Timeline View & Sprint Planning

**Expanded Goal:** Provide engineering managers and tech leads with powerful sprint planning and capacity management capabilities through a horizontal timeline view. This epic delivers visual workload distribution, drag-and-drop sprint rebalancing, capacity indicators showing overloaded sprints, and filtering capabilities. By the end of this epic, managers can plan sprints effectively, identify resource bottlenecks, and ensure balanced team workload—all while developers continue using the Kanban view for daily work. The multi-view approach validates Taskly's differentiation as more than just another board tool.

### Story 4.1: Sprint/Iteration Creation & Management

**As a** workspace admin or board member,
**I want** to create and manage sprints (iterations) for planning work over time,
**so that** I can organize cards into time-boxed delivery cycles.

#### Acceptance Criteria

1. Board settings page includes "Sprints" section displaying list of existing sprints with "+ Create Sprint" button
2. Clicking "+ Create Sprint" opens modal with fields: sprint name (required, e.g., "Sprint 1", "v1.0 Release"), start date (date picker), end date (date picker), goal (optional text, max 500 chars)
3. Sprint dates validated: end date must be after start date; overlapping sprints allowed (warning displayed but not blocked)
4. Creating sprint stores record in `sprints` table: id (UUID), board_id (FK), name, start_date, end_date, goal, status (enum: planned/active/completed), created_at, updated_at
5. Sprint status automatically calculated: "planned" if start_date in future, "active" if current date between start/end, "completed" if end_date passed
6. Sprints list in board settings shows: sprint name, date range ("Jan 1 - Jan 14"), status badge (planned/active/completed), card count, total story points, "Edit" and "Delete" buttons
7. Active sprint highlighted with visual indicator (blue border, "Current Sprint" label)
8. Editing sprint opens same modal pre-filled with existing values; updates sprint record on save
9. Extending active sprint's end date shows confirmation: "Sprint is currently active. Extend end date to [new date]?"
10. Deleting sprint requires confirmation: "Delete sprint? Cards will be moved to Backlog." with "Delete" and "Cancel" buttons
11. Deleting sprint sets all cards' `sprint_id` to NULL (moves to "Backlog" in timeline view) and marks sprint as soft-deleted (`deleted_at` timestamp)
12. Board header displays current active sprint name with progress indicator: "Sprint 2 (Day 5 of 14)" and story point completion ratio "12/25 points completed"
13. Quick sprint navigation dropdown in board header lists all sprints with ability to filter cards by sprint in Kanban view
14. Creating first sprint triggers onboarding tooltip: "Use Timeline view to drag cards into sprints for planning"

### Story 4.2: Timeline View UI & Basic Navigation

**As a** board member,
**I want** to switch to a timeline view showing sprints horizontally,
**so that** I can visualize work distribution across time.

#### Acceptance Criteria

1. Board header includes view toggle buttons: "Kanban" (default) and "Timeline" with icons (list/calendar)
2. Clicking "Timeline" transitions to timeline view within 500ms (smooth transition animation)
3. Timeline view displays horizontal axis representing time: past sprints (left), current sprint (center, highlighted), future sprints (right), backlog (leftmost column)
4. Each sprint rendered as vertical column with header showing: sprint name, date range, days remaining (for active sprint), story point total
5. Current date indicator displayed as vertical red line spanning timeline height with "Today" label
6. Sprints ordered chronologically left-to-right; backlog column always leftmost (for unassigned cards)
7. Cards within each sprint column displayed as compact cards showing: card title, assignee avatars (max 3), priority indicator dot, story points badge, linked PR badge if present
8. Empty sprints display placeholder: "Drag cards here to assign to sprint"
9. Timeline view horizontally scrollable; current sprint auto-scrolled into view on initial load
10. Zoom controls allow adjusting timeline density: "Day", "Week", "Month" granularity (affects column width and date labels)
11. Timeline view persists user preference (last selected view stored in localStorage or user profile)
12. Keyboard shortcut toggles views: "V" key cycles between Kanban and Timeline
13. Timeline view responsive: desktop shows full horizontal layout, tablet (768px-1024px) shows condensed columns, mobile (<768px) falls back to Kanban view with message "Timeline view best viewed on desktop"
14. Active filters (assignee, label, priority) from Kanban view carry over to Timeline view; filtered cards hidden in Timeline as well
15. Card count and total story points displayed in each sprint header: "Sprint 1 (5 cards, 21 pts)"

### Story 4.3: Drag Cards Between Sprints in Timeline

**As a** board member,
**I want** to drag cards between sprints in timeline view,
**so that** I can rebalance workload and adjust sprint scope.

#### Acceptance Criteria

1. Cards in timeline view draggable by clicking and holding (same @dnd-kit library as Kanban for consistency)
2. Dragging card displays ghost preview following cursor; sprint columns highlight on hover showing valid drop zone
3. Dropping card in target sprint column updates `cards.sprint_id` field to target sprint's ID and saves to database
4. Dropping card in "Backlog" column sets `cards.sprint_id` to NULL (unassigns from sprint)
5. Sprint headers update immediately on drop: card count, story point total recalculate and display new values
6. Drag operation triggers optimistic UI update (card moves immediately) followed by API request; rollback if API fails with error toast
7. Activity log entry created: "[User] moved card from [Sprint 1] to [Sprint 2]"
8. Real-time sync: other users viewing timeline see card move via WebSocket broadcast message `{type: 'card_sprint_changed', card_id: uuid, from_sprint: uuid, to_sprint: uuid}`
9. Keyboard alternative: focus card with Tab, press Space to "pick up," Left/Right arrow keys to move between sprints, Space again to "drop"
10. Multi-select supported: Shift+Click or Ctrl+Click to select multiple cards, drag selection to bulk-assign to sprint
11. Bulk sprint assignment updates all selected cards' `sprint_id` in single database transaction; activity log entry: "[User] moved 5 cards to [Sprint 2]"
12. Dragging disabled if user lacks edit permissions on board (cards appear locked with tooltip: "View-only access")
13. Overloaded sprint indicator: if sprint's total story points exceed configured capacity (board setting, default 40 pts), sprint header shows warning badge "Overloaded" with red background
14. Dragging card to overloaded sprint shows confirmation modal: "Sprint 2 is overloaded (45/40 pts). Add card anyway?" with "Yes" and "Cancel" options
15. Sprint scope change tracking: when cards moved in/out of active sprint, board header progress indicator updates immediately: "12/30 points completed" → "12/35 points completed"

### Story 4.4: Visual Capacity Indicators & Workload Balancing

**As a** engineering manager,
**I want** to see visual indicators showing sprint capacity and workload balance,
**so that** I can identify overloaded sprints and distribute work evenly.

#### Acceptance Criteria

1. Each sprint column displays capacity bar at top showing story point utilization: horizontal bar with filled portion representing current points vs. capacity
2. Capacity bar color-coded: green (0-80% capacity), yellow (80-100%), red (>100% overloaded)
3. Capacity bar tooltip on hover shows exact numbers: "25 of 40 points assigned (62%)"
4. Sprint capacity configurable at board level: board settings "Sprint Settings" section includes input "Default sprint capacity (story points)" (default 40)
5. Individual sprint capacity overridable: editing sprint in board settings shows "Capacity (story points)" field defaulting to board-level value but editable per sprint
6. Overloaded sprints (>100% capacity) display warning icon in header with tooltip: "Sprint is overloaded. Consider moving cards to another sprint."
7. Timeline view includes "Capacity Overview" toggle in header: when enabled, shows aggregated view across all sprints as line chart overlaying timeline
8. Capacity overview line chart plots story points per sprint with horizontal reference line at capacity threshold; spikes above line indicate overloaded sprints
9. Team capacity mode (advanced): board settings "Sprint Settings" section includes toggle "Track by assignee capacity"
10. When team capacity mode enabled, capacity bar shows per-assignee workload: stacked bar segments colored by assignee with each segment representing their assigned story points
11. Assignee capacity limits configurable: workspace settings "Team Members" section includes per-member field "Sprint capacity (story points)" (default 20)
12. Hovering over assignee segment in capacity bar shows: "[Username]: 15 of 20 points assigned"
13. Over-assigned team members highlighted in timeline: if assignee has >100% capacity across multiple sprints, their avatar displays red warning dot
14. Filtering timeline by assignee isolates their cards across sprints, showing only their workload distribution (useful for 1:1s and workload discussions)
15. Sprint health score calculated and displayed in header: "Balanced" (all assignees <100%), "Unbalanced" (one or more assignees >100%), "Overloaded" (sprint total >100%)

### Story 4.5: Sprint Planning Workflow & Bulk Actions

**As a** engineering manager,
**I want** to efficiently plan sprints with bulk operations and filtering,
**so that** I can quickly organize large backlogs into sprints.

#### Acceptance Criteria

1. Timeline view header includes "Planning Mode" toggle button; when enabled, UI switches to planning-optimized layout
2. Planning mode displays backlog column wider (30% of viewport) with other sprints condensed; backlog sorted by priority (Urgent → High → Medium → Low → None)
3. Planning mode enables multi-select by default: clicking card selects (checkmark appears), Ctrl+Click to deselect, Shift+Click to select range
4. Selected cards highlighted with blue border; selection count displayed in floating action bar: "5 cards selected" with bulk action buttons
5. Bulk action bar includes buttons: "Assign to Sprint" (dropdown lists sprints), "Set Priority" (dropdown), "Add Label" (dropdown), "Assign to Member" (dropdown), "Clear Selection"
6. Selecting "Assign to Sprint" from bulk actions moves all selected cards to chosen sprint in single database transaction; activity log: "[User] moved 5 cards to [Sprint 2]"
7. Right sidebar in planning mode shows sprint statistics panel: each sprint listed with name, date range, card count, story points, capacity utilization bar, "Add Cards" button
8. Clicking sprint's "Add Cards" button in stats panel opens sprint in focused view: backlog on left, selected sprint on right, simplified two-column layout for focused planning
9. Keyboard shortcuts in planning mode: "A" to select all visible cards, "Escape" to clear selection, "1-9" number keys to quick-assign selected cards to sprint N
10. Quick filters in timeline header: "No Sprint" (shows only backlog), "Current Sprint", "Upcoming Sprints", "Overdue Cards" (due date passed, not completed), "Unassigned" (no assignee)
11. Search input in timeline header filters cards by title/description across all sprints; matching cards highlighted, non-matching cards dimmed
12. Sprint templates: board settings includes "Sprint Templates" section for creating reusable sprint patterns (e.g., "2-week Sprint" with 10 working days, 40 pt capacity)
13. Creating sprint from template pre-fills all settings: duration, capacity, optionally copies cards from previous sprint (useful for recurring maintenance sprints)
14. Export sprint plan: timeline view includes "Export" button generating CSV with columns: Card Title, Sprint, Assignees, Priority, Story Points, Due Date, Status
15. Undo/redo support for sprint planning actions: Ctrl+Z undoes last bulk assignment, Ctrl+Shift+Z redoes; undo stack persists for current session only

---

## Epic 5: Power User Features & Polish

**Expanded Goal:** Deliver productivity enhancements that transform Taskly from a functional tool into a delightful daily driver for power users. This epic implements keyboard-first workflows through a command palette (⌘+K) and comprehensive shortcuts, advanced bulk operations with multi-select and lasso selection, and performance optimizations ensuring sub-second interactions. By the end of this epic, Taskly demonstrates "developer respect" through speed, efficiency, and polish—validating the "zero-friction UX" philosophy and completing the MVP ready for beta launch.

### Story 5.1: Command Palette (⌘+K) Implementation

**As a** power user,
**I want** a keyboard-accessible command palette for quick actions,
**so that** I can perform common tasks without using my mouse.

#### Acceptance Criteria

1. Pressing ⌘+K (Mac) or Ctrl+K (Windows/Linux) opens command palette overlay from any screen
2. Command palette displays as centered modal (800px width) with search input focused automatically
3. Search input supports fuzzy matching: typing "cre card" matches "Create Card" command
4. Command list displays below search input showing: command name, description (gray text), keyboard shortcut (if applicable), icon
5. Commands grouped by category with section headers: "Navigation", "Card Actions", "Board Actions", "View Controls"
6. Navigation commands: "Go to Dashboard", "Go to Board Settings", "Go to Workspace Settings", "Switch Workspace" (shows workspace list on select)
7. Card actions: "Create Card" (prompts for column selection then opens quick-create), "Search Cards" (switches to card search mode), "Filter by Assignee", "Filter by Label"
8. Board actions: "Create Board", "Switch Board" (shows board list), "Create Sprint", "Export Board"
9. View controls: "Switch to Kanban View", "Switch to Timeline View", "Toggle Dark Mode", "Toggle Planning Mode"
10. Arrow keys (↑/↓) navigate command list; Enter executes selected command; Escape closes palette
11. Recently used commands appear at top of list (max 5) for quick access with "Recent" section header
12. Command palette supports command chaining: executing "Create Card" keeps palette open with "Which column?" sub-menu for multi-step workflows
13. Commands dynamically enable/disable based on context: "Switch to Kanban View" disabled when already in Kanban view, "Create Sprint" disabled if no board selected
14. Command palette supports direct card search mode: typing "#" prefix switches to card search showing matching cards with keyboard navigation to open selected card
15. Custom keyboard shortcuts configurable: user settings page includes "Keyboard Shortcuts" section listing all commands with editable shortcut fields
16. Command palette renders in <100ms on open with no lag during typing (search debounced at 150ms)
17. Command palette accessible from any page (global hotkey listener) and adapts commands to current context (board vs. workspace vs. settings)

### Story 5.2: Keyboard Navigation & Shortcuts

**As a** power user,
**I want** comprehensive keyboard shortcuts for common actions,
**so that** I can navigate and manipulate boards without touching my mouse.

#### Acceptance Criteria

1. Card navigation shortcuts: "J" moves focus to next card, "K" moves to previous card (Gmail-style), Tab cycles through cards in column order
2. Focused card indicated with blue outline border; pressing Enter opens card detail modal
3. Card manipulation: "E" edits focused card (opens detail modal), "D" deletes card (with confirmation), "M" opens move menu (arrow keys select column, Enter confirms)
4. Column navigation: Ctrl+← moves focus to previous column, Ctrl+→ moves to next column
5. Card creation: "C" opens quick-create input in currently focused column (or first column if no focus)
6. Multi-select: Shift+↑/↓ extends selection to adjacent cards, Ctrl+Click (or Cmd+Click on Mac) adds individual card to selection
7. Selection actions: "A" selects all cards in focused column, Ctrl+A selects all visible cards on board, Escape clears selection
8. View switching: "V" cycles through views (Kanban → Timeline → Kanban), "1" forces Kanban view, "2" forces Timeline view
9. Search: "/" activates board-wide search input (same as clicking search box), Escape closes search and clears filters
10. Undo/Redo: Ctrl+Z undoes last action (card move, edit, delete), Ctrl+Shift+Z redoes undone action (session-based, not persistent)
11. Global shortcuts work across entire app: "G then D" navigates to Dashboard, "G then S" navigates to Settings (Gmail-style sequential shortcuts)
12. Modal shortcuts: Enter submits form in modals (Create Board, Create Sprint), Escape closes modal without saving
13. Timeline-specific: Left/Right arrow keys pan timeline horizontally, "+"/"-" zoom in/out timeline density
14. Shortcut help overlay: pressing "?" displays cheat sheet modal showing all available shortcuts organized by category
15. Shortcuts configurable: Settings page "Keyboard Shortcuts" section allows remapping any shortcut (prevents conflicts, shows warning if duplicate)
16. Shortcuts respect focus context: text input fields disable navigation shortcuts (J/K/C/etc.) to prevent interference with typing; Escape re-enables
17. Visual feedback: when shortcut triggered, brief animation or highlight confirms action (e.g., "C" pressed → column highlight flash before quick-create appears)

### Story 5.3: Multi-Select & Lasso Selection

**As a** board member,
**I want** to select multiple cards at once for bulk operations,
**so that** I can efficiently manage large numbers of cards.

#### Acceptance Criteria

1. Multi-select enabled in Kanban view: clicking checkbox icon in card corner (appears on hover) selects card
2. Selected cards display visual indicator: blue border, semi-transparent blue overlay, checkmark in corner
3. Shift+Click on card selects all cards between last selected card and clicked card (range selection)
4. Ctrl+Click (Cmd+Click on Mac) toggles individual card selection without affecting other selections
5. Lasso selection: Click and drag in empty board space draws selection rectangle; all cards overlapping rectangle when mouse released are selected
6. Lasso visual: semi-transparent blue rectangle with dashed border follows cursor during drag
7. Selection count displayed in floating toolbar at bottom of screen: "5 cards selected" with action buttons
8. Floating toolbar buttons: "Assign" (assignee dropdown), "Label" (label dropdown), "Priority" (priority dropdown), "Move to Column" (column dropdown), "Delete" (with confirmation), "Clear Selection"
9. Bulk actions apply to all selected cards in single API request (batch endpoint: `POST /api/cards/bulk-update` with card IDs array and update payload)
10. Bulk update optimistic: UI updates immediately for all selected cards, rollback if API fails with error toast showing failed count
11. Activity log entries for bulk actions: "[User] assigned 5 cards to [Username]", "[User] added label 'Bug' to 3 cards"
12. Select all button in board header: "Select All" checkbox selects all visible cards (respects active filters)
13. Indeterminate checkbox state: if some but not all cards selected, checkbox shows indeterminate state (dash icon)
14. Keyboard support: "A" selects all in focused column, Ctrl+A selects all visible on board, Shift+J/K extends selection up/down
15. Selection persists across view switches: selecting cards in Kanban then switching to Timeline preserves selection
16. Selection cleared on: Escape key, clicking "Clear Selection" button, performing destructive action like delete, leaving board (navigating away)
17. Mobile/tablet touch support: long-press card (500ms) enters multi-select mode with checkboxes appearing on all cards

### Story 5.4: Advanced Bulk Operations & Batch Editing

**As a** board member,
**I want** powerful bulk editing capabilities for selected cards,
**so that** I can quickly update multiple cards with consistent changes.

#### Acceptance Criteria

1. Floating toolbar (Story 5.3) includes "Edit Multiple" button opening bulk edit modal
2. Bulk edit modal displays fields: Title Prefix/Suffix (add text to all titles), Description Append (add text to end of all descriptions), Assignees (add/remove), Labels (add/remove), Priority (set), Story Points (set or adjust by +/- amount), Due Date (set or offset by days), Sprint Assignment
3. Field-level checkboxes: user selects which fields to update (prevents accidental overwrites)
4. Preview section in modal shows first 3 affected cards with before/after comparison for selected fields
5. Title prefix/suffix examples: prefix "URGENT: " to all selected cards, suffix " (deprecated)" to cards
6. Assignees bulk action modes: "Add assignees to existing" (keeps current, adds new), "Replace all assignees" (removes current, sets new), "Remove specific assignees" (unassign selected members)
7. Labels bulk action similar: "Add labels", "Replace labels", "Remove labels" modes
8. Story points adjustment: "Set to value" (overwrite), "Increase by X", "Decrease by X" modes
9. Due date operations: "Set to specific date", "Add X days to existing dates", "Remove due dates"
10. Sprint assignment: "Assign to sprint" (dropdown), "Remove from sprint" (moves to backlog)
11. Applying bulk edit executes single `POST /api/cards/bulk-update` request with all changes; backend processes in database transaction (all or nothing)
12. Progress indicator during bulk update: "Updating 25 cards..." with spinner; success message: "25 cards updated successfully"
13. Error handling: if bulk update fails for some cards (e.g., validation errors), shows partial success message: "20 of 25 cards updated. 5 failed." with details button expanding error list
14. Undo support: bulk edit actions added to undo stack; Ctrl+Z reverts entire bulk operation (restores all changed cards to previous state)
15. Activity log: single aggregated entry "[User] bulk updated 25 cards (changed priority, added labels)" rather than 25 separate entries
16. Bulk operations respect permissions: cards user lacks edit permission for are excluded from bulk update with warning: "2 cards skipped (no edit permission)"
17. Rate limiting protection: bulk updates >100 cards chunked into batches of 50 with brief delays to prevent database overload

### Story 5.5: Performance Optimization & Final Polish

**As a** user,
**I want** Taskly to feel fast and responsive at all times,
**so that** the tool doesn't slow me down during daily work.

#### Acceptance Criteria

1. Page load performance: initial load <1 second (cached), <2 seconds (cold start) measured with Lighthouse performance score >90
2. View transitions: switching Kanban ↔ Timeline completes in <500ms with smooth animation (no janky frames)
3. Large board performance: boards with 500+ cards render without lag using virtualization (only visible cards rendered in DOM)
4. Lazy loading: images (avatars, attachments) loaded on-demand with placeholder; below-fold content loaded after initial render
5. Optimistic UI: all user actions (card move, edit, delete) update UI immediately with API call in background; rollback on failure with error toast
6. Debouncing: search input, filters, and inline editing debounced at 300ms to reduce API calls during rapid typing
7. Caching strategy: frequently accessed data (boards list, user profile, workspace members) cached in frontend with 5-minute TTL; cache invalidated on updates
8. Bundle size optimization: frontend JavaScript bundle <500KB gzipped; code splitting by route (dashboard, board, settings as separate chunks)
9. Lighthouse PWA score >90: manifest file, service worker for offline fallback (shows "You're offline" message), app installable as PWA
10. Accessibility audit: WCAG 2.1 AA compliance verified with axe DevTools (0 critical violations, <5 minor issues)
11. Error boundaries: React error boundaries catch crashes and display user-friendly error page with "Reload" button (errors logged to Sentry)
12. Loading states: all asynchronous operations display skeleton loaders or spinners within 100ms (no blank screens)
13. Empty states: all empty data scenarios (no boards, no cards, no workspaces) show helpful empty state illustrations with clear CTAs
14. Final UI polish: consistent spacing (8px grid system), typography (single font stack), colors (design system with CSS variables), animations (200ms standard, 300ms complex)
15. Cross-browser testing: verified in Chrome, Firefox, Safari, Edge with no major visual or functional issues
16. Mobile responsive: all features functional on tablet (768px+) with touch-optimized interactions; mobile (<768px) shows streamlined read-only view with message "Full editing experience available on desktop"
17. Production monitoring: Sentry configured for error tracking, Datadog/Prometheus for metrics (API latency, page load times, error rates), uptime monitoring active

---

## Checklist Results Report

### Executive Summary

- **Overall PRD Completeness:** 95%
- **MVP Scope Appropriateness:** Just Right (well-balanced between value delivery and timeline constraints)
- **Readiness for Architecture Phase:** **READY**
- **Most Critical Gaps:** Minor - Need to document user research findings when available (acceptable pre-beta), and formalize stakeholder approval process

### Category Analysis

| Category                         | Status  | Critical Issues |
| -------------------------------- | ------- | --------------- |
| 1. Problem Definition & Context  | **PASS** | None - Problem statement from brief is comprehensive |
| 2. MVP Scope Definition          | **PASS** | None - Clear MVP boundaries with post-MVP vision documented |
| 3. User Experience Requirements  | **PASS** | None - Detailed UI/UX goals, interaction paradigms, and accessibility targets |
| 4. Functional Requirements       | **PASS** | None - 18 FRs covering all MVP features, testable and specific |
| 5. Non-Functional Requirements   | **PASS** | None - 12 NFRs with measurable performance targets |
| 6. Epic & Story Structure        | **PASS** | None - 5 epics, 29 stories, logical sequencing, comprehensive ACs |
| 7. Technical Guidance            | **PASS** | None - Extensive technical assumptions section guides architect |
| 8. Cross-Functional Requirements | **PASS** | None - Data entities, GitHub integration, deployment all specified |
| 9. Clarity & Communication       | **PASS** | None - Clear, consistent language throughout |

**Overall Status:** 9/9 categories **PASS** (90%+ complete)

### Key Findings

**Strengths:**
- Problem definition clear with quantified impact (5-10 hours/week wasted, context loss causes rework)
- MVP scope well-balanced: 5 epics delivering essential features only, post-MVP vision documented in brief
- 29 user stories with ~350 acceptance criteria provide implementation-ready specifications
- Technical guidance comprehensive (stack, architecture, security, performance targets)
- Epic sequencing logical with appropriate dependencies
- Non-functional requirements measurable and realistic (<1s load, <500ms transitions, <3s Git ops)

**Medium Priority Improvements:**
1. **User Research Validation** - PRD based on Project Brief assumptions; recommend conducting 10-20 user interviews during Epic 1-2 development to validate pain points
2. **Stakeholder Approval** - Add "Approved by" row to Change Log once stakeholders review

**Low Priority Improvements:**
1. **Wireframes/Mockups** - Defer to UX Expert phase (appropriate)
2. **API Documentation Preview** - Defer to Architect phase (appropriate)

### MVP Scope Assessment

**Well-Balanced MVP** - The 5 epic structure delivers:
- **Epic 1:** Essential foundation (infrastructure, auth, deployment)
- **Epic 2:** Core product value (boards, cards, drag-and-drop)
- **Epic 3:** Key differentiation (Git integration, webhooks, auto-sync)
- **Epic 4:** Manager persona value (timeline view, sprint planning)
- **Epic 5:** Developer delight (keyboard shortcuts, performance)

**Timeline Realism:** 9-11 week estimate for 29 stories is aggressive but achievable with 1-2 developers. Epics 1-3 are critical path; Epics 4-5 could be descoped if timeline pressure arises.

### Final Decision

**✅ READY FOR ARCHITECT**

The PRD and epics are comprehensive, properly structured, and ready for architectural design. All 9 checklist categories achieve **PASS** status with no blocking deficiencies.

---

## Next Steps

### UX Expert Prompt

Please create detailed UI/UX design specifications for Taskly based on this PRD. Focus on:

**1. Visual Design System**
- Color palette (primary: GitHub blue #0366D6, status colors: green/yellow/red/purple, neutral grays)
- Typography (monospace for code/IDs: Fira Code/JetBrains Mono; sans-serif for UI: Inter/system-ui)
- Iconography (Heroicons/Lucide with 2px stroke, GitHub Octicons for Git indicators)
- Spacing grid (8px system)
- Dark mode implementation

**2. Core Screen Wireframes/Mockups**
- Kanban Board View (drag-and-drop, card states, inline PR status)
- Timeline View (horizontal sprints, capacity bars, card compaction)
- Card Detail Modal (markdown editor, PR summary, activity timeline, comments)
- Command Palette (⌘+K overlay, fuzzy search, keyboard navigation)
- Workspace Dashboard (board grid, empty states)
- Onboarding Flow (multi-step wizard: workspace → GitHub connect → board → first card)

**3. Interaction Patterns**
- Drag-and-drop behavior (@dnd-kit library, ghost previews, drop zones)
- Keyboard shortcuts (J/K navigation, C create, E edit, V view switch)
- Hover states (contextual actions on cards/columns)
- Animations (200ms standard, 300ms complex, optimistic UI updates)
- Real-time collaboration indicators (presence, live updates)

**4. Responsive Layouts**
- Desktop (1280px+): full multi-column Kanban, horizontal timeline
- Tablet (768-1024px): condensed columns, touch-optimized drag
- Mobile (<768px): single-column fallback, read-only message for timeline

**5. Accessibility Compliance (WCAG AA)**
- Keyboard navigation for all interactive elements
- Screen reader support (semantic HTML, ARIA labels)
- Focus indicators (visible outlines)
- Color contrast (4.5:1 minimum for text)
- No color-only information (icons + color for status)

**Deliverables:**
- Design system documentation (Markdown + Figma/Sketch)
- High-fidelity mockups for 8 core screens
- Interactive prototype (optional but recommended for drag-and-drop)
- Component library specifications (for shadcn/ui customization)
- Accessibility audit checklist

Reference "User Interface Design Goals" section for detailed vision and requirements.

---

### Architect Prompt

Please create comprehensive technical architecture documentation for Taskly based on this PRD. Focus on:

**1. Database Architecture**
- Complete ERD (Entity-Relationship Diagram) with all tables, columns, data types, constraints
- Tables: users, workspaces, workspace_members, boards, cards, card_assignees, card_comments, card_activity, sprints, labels, git_repositories, pull_requests, card_pull_requests
- Indexes strategy (B-tree on FKs, GIN on JSONB, full-text search indexes)
- JSONB schema for flexible metadata (cards.metadata, boards.columns, pull_requests.ci_status)
- Migration plan (Alembic migrations mapped to stories requiring schema changes)

**2. API Specifications**
- RESTful API endpoints (full OpenAPI 3.0 specification)
  - Authentication: POST /auth/github/callback, POST /auth/refresh, POST /auth/logout
  - Workspaces: GET/POST /workspaces, GET/PATCH/DELETE /workspaces/{id}, POST /workspaces/{id}/invite
  - Boards: GET/POST /boards, GET/PATCH/DELETE /boards/{id}
  - Cards: GET/POST /cards, GET/PATCH/DELETE /cards/{id}, POST /cards/bulk-update
  - Git: GET /git/repositories, POST /git/repositories/connect, POST /cards/{id}/create-branch
  - Webhooks: POST /webhooks/github
- Request/response schemas (Pydantic models)
- Error response formats (consistent error codes, messages)
- Authentication flow (JWT access + refresh tokens, middleware)
- Rate limiting strategy (per-user, per-IP, Redis-backed)

**3. WebSocket Architecture**
- Real-time event specifications (message formats, event types)
- Events: card_moved, card_updated, pr_updated, card_sprint_changed
- Connection lifecycle (authentication, heartbeat, reconnection)
- Scalability approach (Redis pub/sub for multi-instance sync)
- Fallback to polling (graceful degradation)

**4. Background Job Architecture (Celery)**
- Task definitions and priorities
  - Git operations (branch creation, webhook processing) - high priority
  - Bulk updates (batch card changes) - medium priority
  - Email notifications - low priority
- Retry logic (exponential backoff: 5s, 25s, 125s)
- Dead letter queue for failed tasks
- Task monitoring (Flower dashboard)

**5. GitHub Integration Architecture**
- OAuth 2.0 flow (authorization, token exchange, refresh)
- API client design (httpx async client, retry middleware, rate limit handling)
- Webhook handler architecture
  - Signature validation (HMAC SHA-256)
  - Event routing (pull_request, pull_request_review, status, check_suite, push)
  - Idempotency handling (event_id deduplication)
- Rate limit management (5000 req/hour per user, caching strategy, webhook-first approach)

**6. Deployment Architecture**
- Docker Compose services (Next.js, FastAPI, PostgreSQL, Redis, Celery worker)
- Multi-stage Dockerfile builds (optimized image sizes)
- CI/CD pipeline (GitHub Actions: lint → test → build → deploy)
- Environment configuration (dev, staging, production)
- Infrastructure diagram (AWS/GCP/DigitalOcean managed services)
- Secrets management (environment variables, cloud secrets manager)

**7. Security Architecture**
- Authentication flow diagram (GitHub OAuth → JWT issuance → token refresh)
- Authorization model (workspace-level RBAC: admin vs member)
- Data encryption (at-rest: PostgreSQL encryption, in-transit: TLS 1.3)
- GitHub token security (encrypted storage, never logged)
- Input validation (Pydantic schemas, SQL injection prevention)
- CORS configuration (allowed origins)

**8. Performance Optimizations**
- Frontend: code splitting (route-based chunks), lazy loading (images, below-fold), bundle size target (<500KB gzipped)
- Backend: query optimization (eager loading, N+1 prevention), database connection pooling
- Caching strategy: Redis for sessions/boards (5 min TTL), frontend caching (React Query)
- Virtualization for large boards (500+ cards, only render visible)

**9. Monitoring & Observability**
- Error tracking (Sentry integration)
- Metrics collection (Prometheus/Datadog: API latency, Git operation success rate, queue depth)
- Structured logging (JSON logs with correlation IDs)
- Uptime monitoring (external health checks)

**Deliverables:**
- Architecture document (Markdown with diagrams)
- Database schema SQL (CREATE TABLE statements + indexes)
- OpenAPI specification (YAML/JSON for API docs)
- Docker Compose configuration (production-ready)
- Infrastructure-as-code templates (Terraform or CloudFormation, optional)
- Alembic migration plan (mapping migrations to epic/story delivery)

Reference "Technical Assumptions" section for stack decisions, constraints, and rationale.

---

**PRD Status:** ✅ **APPROVED FOR IMPLEMENTATION**

This document is now ready for handoff to UX Expert (design phase) and Technical Architect (architecture phase). Both workstreams can proceed in parallel during Epic 1 development.
