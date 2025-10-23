# Epic 5: Power User Features & Polish

**Expanded Goal:** Deliver productivity enhancements that transform Taskly from a functional tool into a delightful daily driver for power users. This epic implements keyboard-first workflows through a command palette (⌘+K) and comprehensive shortcuts, advanced bulk operations with multi-select and lasso selection, and performance optimizations ensuring sub-second interactions. By the end of this epic, Taskly demonstrates "developer respect" through speed, efficiency, and polish—validating the "zero-friction UX" philosophy and completing the MVP ready for beta launch.

## Story 5.1: Command Palette (⌘+K) Implementation

**As a** power user,
**I want** a keyboard-accessible command palette for quick actions,
**so that** I can perform common tasks without using my mouse.

### Acceptance Criteria

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

## Story 5.2: Keyboard Navigation & Shortcuts

**As a** power user,
**I want** comprehensive keyboard shortcuts for common actions,
**so that** I can navigate and manipulate boards without touching my mouse.

### Acceptance Criteria

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

## Story 5.3: Multi-Select & Lasso Selection

**As a** board member,
**I want** to select multiple cards at once for bulk operations,
**so that** I can efficiently manage large numbers of cards.

### Acceptance Criteria

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

## Story 5.4: Advanced Bulk Operations & Batch Editing

**As a** board member,
**I want** powerful bulk editing capabilities for selected cards,
**so that** I can quickly update multiple cards with consistent changes.

### Acceptance Criteria

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

## Story 5.5: Performance Optimization & Final Polish

**As a** user,
**I want** Taskly to feel fast and responsive at all times,
**so that** the tool doesn't slow me down during daily work.

### Acceptance Criteria

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
