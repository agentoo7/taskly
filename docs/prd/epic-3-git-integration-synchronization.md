# Epic 3: Git Integration & Synchronization

**Expanded Goal:** Implement bidirectional Git-native synchronization that connects Taskly boards directly to GitHub repositories. This epic delivers the core product differentiation: automatic branch creation from cards, card-to-PR linking with auto-detection, webhook-based real-time sync showing PR status and CI results inline on cards, and automatic card movement when PRs merge. By the end of this epic, Taskly transforms from a standalone project management tool into a Git-native "control surface for your repo," eliminating double-entry and preserving task-to-code context automatically.

## Story 3.1: GitHub Repository Connection

**As a** workspace admin,
**I want** to connect GitHub repositories to my workspace,
**so that** boards can integrate with code repositories.

### Acceptance Criteria

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

## Story 3.2: Manual Card-to-PR Linking

**As a** board member,
**I want** to manually link cards to GitHub pull requests by pasting PR URLs,
**so that** I can connect existing work to cards.

### Acceptance Criteria

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

## Story 3.3: One-Click Branch Creation from Cards

**As a** board member,
**I want** to create GitHub branches directly from cards with one click,
**so that** I can start coding without manual branch creation steps.

### Acceptance Criteria

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

## Story 3.4: Webhook Infrastructure & PR Status Sync

**As a** system,
**I want** to receive GitHub webhooks and update card PR status in real-time,
**so that** boards always reflect current code state without manual updates.

### Acceptance Criteria

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

## Story 3.5: Auto-Display PR Status & Commits on Cards

**As a** board member,
**I want** to see PR status, commits, and CI results inline on cards,
**so that** I have full context without leaving the board.

### Acceptance Criteria

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

## Story 3.6: Auto-Move Cards on PR Merge

**As a** board member,
**I want** cards to automatically move to "Done" when linked PRs are merged,
**so that** the board reflects code completion without manual updates.

### Acceptance Criteria

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

## Story 3.7: Card ID Auto-Detection in Branch/PR Names

**As a** board member,
**I want** Taskly to automatically detect when PRs or branches reference card IDs,
**so that** I don't have to manually link every PR.

### Acceptance Criteria

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
