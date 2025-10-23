# External APIs

## GitHub REST API v3

- **Purpose:** Repository management, branch creation, pull request data fetching, user profile access
- **Documentation:** https://docs.github.com/en/rest
- **Base URL:** `https://api.github.com`
- **Authentication:** OAuth 2.0 Bearer tokens
- **Rate Limits:** 5,000 requests/hour per authenticated user

**Key Endpoints Used:**
- `GET /user` - Fetch authenticated user profile
- `GET /user/repos` - List user's accessible repositories
- `POST /repos/{owner}/{repo}/git/refs` - Create branch
- `GET /repos/{owner}/{repo}/pulls/{pr_number}` - Fetch PR details
- `GET /repos/{owner}/{repo}/commits/{sha}/status` - Get commit status

**Integration Notes:**
- **Caching:** PR data (5 min TTL), repository metadata (1 hour TTL)
- **Error Handling:** 401 → refresh token, 403 → rate limit (show stale data), 502/503 → retry with backoff
- **Circuit Breaker:** After 5 consecutive failures, pause API calls for 60s

## GitHub OAuth 2.0

- **Purpose:** User authentication and authorization
- **Documentation:** https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps
- **Flow Type:** Authorization Code Grant

**OAuth Flow:**
1. Redirect user to `https://github.com/login/oauth/authorize`
2. GitHub redirects back with authorization code
3. Exchange code for access token via `POST https://github.com/login/oauth/access_token`
4. Fetch user profile with access token

**Integration Notes:**
- Token storage: Encrypt access_token before storing in database (AES-256)
- CSRF protection via `state` parameter validation

## GitHub Webhooks

- **Purpose:** Real-time notifications for repository events
- **Documentation:** https://docs.github.com/en/webhooks
- **Delivery Method:** HTTP POST to `https://taskly.app/api/webhooks/github`
- **Authentication:** HMAC-SHA256 signature validation

**Events Subscribed:**
- `pull_request` (opened, closed, edited, ready_for_review)
- `pull_request_review` (submitted, dismissed)
- `status` / `check_suite` (CI status updates)
- `push` (commits to PR branches)

**Processing Flow:**
1. Receive webhook POST
2. Validate HMAC signature
3. Check idempotency (event_id in Redis)
4. Enqueue to Celery task
5. Return 200 OK immediately

**Integration Notes:**
- Idempotency: Store delivery ID in Redis (24-hour TTL)
- Timeout: Respond within 10s to prevent GitHub retries
- Retry logic: 3 attempts with exponential backoff

---
