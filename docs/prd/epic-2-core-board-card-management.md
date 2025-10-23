# Epic 2: Core Board & Card Management

**Expanded Goal:** Enable users to create workspaces, invite team members, and manage visual Kanban boards with rich card metadata. This epic delivers the core project management experience with drag-and-drop card manipulation, comprehensive metadata support (assignees, labels, priorities, story points, due dates), card comments, and activity tracking. By the end of this epic, Taskly functions as a complete standalone project management tool comparable to Trello, providing immediate value even without Git integration.

## Story 2.1: Workspace Creation & Management

**As a** logged-in user,
**I want** to create and manage workspaces for my teams,
**so that** I can organize multiple projects separately.

### Acceptance Criteria

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

## Story 2.2: Team Member Invitations & Permissions

**As a** workspace admin,
**I want** to invite team members via email and manage their permissions,
**so that** my team can collaborate on boards.

### Acceptance Criteria

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

## Story 2.3: Board Creation & Column Customization

**As a** workspace member,
**I want** to create boards with customizable columns,
**so that** I can organize cards according to my team's workflow.

### Acceptance Criteria

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

## Story 2.4: Card Creation & Basic Metadata

**As a** board member,
**I want** to create cards with title, description, and basic metadata,
**so that** I can capture and organize tasks.

### Acceptance Criteria

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

## Story 2.5: Drag-and-Drop Card Movement

**As a** board member,
**I want** to drag cards between columns and reorder them within columns,
**so that** I can visualize workflow progress.

### Acceptance Criteria

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

## Story 2.6: Advanced Card Metadata (Assignees & Labels)

**As a** board member,
**I want** to assign cards to team members and add labels,
**so that** I can categorize and distribute work effectively.

### Acceptance Criteria

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

## Story 2.7: Card Comments & Activity Timeline

**As a** board member,
**I want** to comment on cards and see activity history,
**so that** I can collaborate and track changes.

### Acceptance Criteria

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
