# REST API Specification

Complete OpenAPI 3.0 specification available in full document. Key endpoints:

**Authentication:**
- `GET /auth/github/login` - Initiate OAuth
- `GET /auth/github/callback` - OAuth callback
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout user

**Workspaces:**
- `GET /workspaces` - List user's workspaces
- `POST /workspaces` - Create workspace
- `GET /workspaces/{id}` - Get workspace details
- `PATCH /workspaces/{id}` - Update workspace
- `DELETE /workspaces/{id}` - Delete workspace

**Boards:**
- `GET /boards` - List boards in workspace
- `POST /boards` - Create board
- `GET /boards/{id}` - Get board with cards

**Cards:**
- `POST /cards` - Create card
- `GET /cards/{id}` - Get card details
- `PATCH /cards/{id}` - Update card
- `DELETE /cards/{id}` - Delete card
- `POST /cards/bulk-update` - Bulk update cards
- `POST /cards/{id}/create-branch` - Create GitHub branch

**Git Integration:**
- `POST /webhooks/github` - GitHub webhook receiver

**Response Format:** RFC 7807 Problem Details for errors

---
