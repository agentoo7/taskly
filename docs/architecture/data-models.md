# Data Models

## 1. User

**Purpose:** Represents authenticated users who access Taskly via GitHub OAuth.

**Key Attributes:**
- `id`: UUID - Primary identifier
- `github_id`: Integer - GitHub user ID (unique, from OAuth)
- `username`: String - GitHub username
- `email`: String - User email (from GitHub profile)
- `avatar_url`: String - GitHub avatar URL
- `github_access_token`: String - Encrypted OAuth token for GitHub API calls
- `created_at`: DateTime - Account creation timestamp
- `updated_at`: DateTime - Last profile update

**Relationships:**
- One user can belong to **many workspaces** (via `workspace_members` join table)
- One user can be assigned to **many cards** (via `card_assignees` join table)
- One user **creates** many cards, comments, activity entries

## 2. Workspace

**Purpose:** Top-level organizational container for boards and team collaboration.

**Key Attributes:**
- `id`: UUID - Primary identifier
- `name`: String (max 100 chars) - Workspace display name
- `created_by`: UUID - Foreign key to User (workspace creator)
- `created_at`: DateTime - Creation timestamp
- `updated_at`: DateTime - Last modification

**Relationships:**
- Belongs to **one creator** (User)
- Has **many members** (Users via `workspace_members` with roles)
- Contains **many boards**
- Has **many connected git repositories**

## 3. Board

**Purpose:** Kanban board with customizable columns for organizing cards.

**Key Attributes:**
- `id`: UUID - Primary identifier
- `workspace_id`: UUID - Foreign key to Workspace
- `name`: String (max 100 chars) - Board display name
- `columns`: JSONB - Array of column definitions: `[{id, name, position}]`
- `default_repository_id`: UUID - Optional FK to GitRepository (for branch creation)
- `archived`: Boolean - Soft delete flag
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships:**
- Belongs to **one workspace**
- Contains **many cards**
- Has **many sprints**
- May link to **one default git repository**

## 4. Card

**Purpose:** Central entity representing a task/feature with rich metadata.

**Key Attributes:**
- `id`: UUID - Primary identifier
- `board_id`: UUID - Foreign key to Board
- `column_id`: UUID - Current column (references Board.columns JSONB)
- `title`: String (max 255 chars) - Card title
- `description`: Text - Markdown description
- `metadata`: JSONB - Flexible storage: `{labels: [{id, name, color}], acceptance_criteria: "text"}`
- `priority`: Enum('none', 'low', 'medium', 'high', 'urgent') - Priority level
- `story_points`: Integer (0-99) - Estimation
- `due_date`: Date - Optional deadline
- `position`: Integer - Position within column (for ordering)
- `sprint_id`: UUID - Optional FK to Sprint (null = backlog)
- `created_by`: UUID - FK to User
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships:**
- Belongs to **one board**
- Positioned in **one column** (within board)
- Assigned to **many users** (via `card_assignees`)
- Linked to **many pull requests** (via `card_pull_requests`)
- Optionally assigned to **one sprint**
- Has **many comments**
- Has **many activity entries**

## 5. Sprint

**Purpose:** Time-boxed iteration for organizing cards and capacity planning.

**Key Attributes:**
- `id`: UUID - Primary identifier
- `board_id`: UUID - Foreign key to Board
- `name`: String - Sprint name (e.g., "Sprint 1", "v1.0 Release")
- `start_date`: Date - Sprint start
- `end_date`: Date - Sprint end
- `goal`: Text (max 500 chars) - Optional sprint goal description
- `capacity_points`: Integer - Configurable capacity (default 40 story points)
- `status`: Enum('planned', 'active', 'completed') - Calculated from dates
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime - Soft delete timestamp

**Relationships:**
- Belongs to **one board**
- Contains **many cards** (cards.sprint_id points here)

## 6. GitRepository

**Purpose:** Caches connected GitHub repository metadata.

**Key Attributes:**
- `id`: UUID - Primary identifier
- `workspace_id`: UUID - FK to Workspace
- `github_repo_id`: Integer - GitHub's repository ID (unique)
- `owner`: String - GitHub owner/org name
- `name`: String - Repository name
- `full_name`: String - owner/repo format
- `default_branch`: String - Main branch name (e.g., "main")
- `is_active`: Boolean - Soft delete flag (disconnected repos)
- `connected_at`: DateTime
- `updated_at`: DateTime

**Relationships:**
- Belongs to **one workspace**
- Has **many pull requests**
- May be default repository for **many boards**

## 7. PullRequest

**Purpose:** Caches GitHub PR data to reduce API calls and enable fast queries.

**Key Attributes:**
- `id`: UUID - Primary identifier
- `repository_id`: UUID - FK to GitRepository
- `github_pr_id`: Integer - GitHub's PR ID
- `pr_number`: Integer - PR number (e.g., #123)
- `title`: String - PR title
- `state`: Enum('open', 'closed', 'draft', 'merged') - PR state
- `author_github_id`: Integer - GitHub user ID of PR author
- `head_branch`: String - Source branch
- `base_branch`: String - Target branch
- `url`: String - GitHub PR URL
- `mergeable`: Boolean - Can be merged?
- `ci_status`: JSONB - CI check results: `{status: 'success'|'failure'|'pending', checks: [{name, status, url}]}`
- `commit_count`: Integer - Number of commits
- `last_commit_sha`: String - Latest commit SHA
- `approval_count`: Integer - Number of approving reviews
- `fetched_at`: DateTime - Last sync from GitHub
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships:**
- Belongs to **one git repository**
- Linked to **many cards** (via `card_pull_requests`)

## Additional Supporting Models

- **WorkspaceMember:** Join table linking workspaces ↔ users with roles
- **CardPullRequest:** Join table linking cards ↔ pull requests
- **CardAssignee:** Join table linking cards ↔ users (assignees)
- **CardComment:** Comments on cards
- **CardActivity:** Audit log for card changes

---
