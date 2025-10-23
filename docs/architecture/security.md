# Security

## Input Validation

- **Library:** Pydantic (integrated with FastAPI)
- **Location:** API boundary (validate before processing)
- **Rules:** Whitelist approach, reject invalid with 400/422

## Authentication & Authorization

- **Auth Method:** GitHub OAuth 2.0 + JWT tokens
- **Session Management:** 15 min access tokens, 7 day refresh tokens
- **Required Patterns:** All endpoints require JWT (except auth, health, webhooks)

## Secrets Management

- **Development:** `.env` file (not committed)
- **Production:** Environment variables (encrypted)
- **Code Requirements:** Never hardcode secrets, access via Settings class only

## API Security

- **Rate Limiting:** 100 req/min per user, 1000 req/min per IP (Redis-backed)
- **CORS Policy:** Restrict origins to frontend domains
- **Security Headers:** X-Content-Type-Options, X-Frame-Options, HSTS
- **HTTPS Enforcement:** TLS 1.3 via DigitalOcean Load Balancer

## Data Protection

- **Encryption at Rest:** PostgreSQL managed service (provider-managed)
- **Encryption in Transit:** TLS 1.3 for all connections
- **PII Handling:** Minimal collection, right to deletion, data export
- **Logging Restrictions:** Never log passwords, tokens, API keys

## Dependency Security

- **Scanning Tool:** Dependabot (GitHub native)
- **Update Policy:** Security patches within 48 hours

---
