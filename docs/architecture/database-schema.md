# Database Schema

Complete PostgreSQL 15+ schema with:
- UUID primary keys
- JSONB columns for flexible metadata
- Enum types for constrained values
- Foreign key constraints with cascade rules
- Optimized indexes (B-tree, GIN, composite)

Core tables:
- `users`, `workspaces`, `workspace_members`
- `boards`, `cards`, `card_assignees`, `card_comments`, `card_activity`
- `sprints`
- `git_repositories`, `pull_requests`, `card_pull_requests`
- `refresh_tokens`

**Migration Strategy:** Alembic migrations mapped to epic/story delivery

---
