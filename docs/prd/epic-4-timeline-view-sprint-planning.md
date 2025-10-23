# Epic 4: Timeline View & Sprint Planning

**Expanded Goal:** Provide engineering managers and tech leads with powerful sprint planning and capacity management capabilities through a horizontal timeline view. This epic delivers visual workload distribution, drag-and-drop sprint rebalancing, capacity indicators showing overloaded sprints, and filtering capabilities. By the end of this epic, managers can plan sprints effectively, identify resource bottlenecks, and ensure balanced team workload—all while developers continue using the Kanban view for daily work. The multi-view approach validates Taskly's differentiation as more than just another board tool.

## Story 4.1: Sprint/Iteration Creation & Management

**As a** workspace admin or board member,
**I want** to create and manage sprints (iterations) for planning work over time,
**so that** I can organize cards into time-boxed delivery cycles.

### Acceptance Criteria

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

## Story 4.2: Timeline View UI & Basic Navigation

**As a** board member,
**I want** to switch to a timeline view showing sprints horizontally,
**so that** I can visualize work distribution across time.

### Acceptance Criteria

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

## Story 4.3: Drag Cards Between Sprints in Timeline

**As a** board member,
**I want** to drag cards between sprints in timeline view,
**so that** I can rebalance workload and adjust sprint scope.

### Acceptance Criteria

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

## Story 4.4: Visual Capacity Indicators & Workload Balancing

**As a** engineering manager,
**I want** to see visual indicators showing sprint capacity and workload balance,
**so that** I can identify overloaded sprints and distribute work evenly.

### Acceptance Criteria

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

## Story 4.5: Sprint Planning Workflow & Bulk Actions

**As a** engineering manager,
**I want** to efficiently plan sprints with bulk operations and filtering,
**so that** I can quickly organize large backlogs into sprints.

### Acceptance Criteria

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
