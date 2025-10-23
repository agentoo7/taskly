# Test Strategy and Standards

## Testing Philosophy

- **Approach:** Test-After Development (TAD) with high coverage
- **Coverage Goals:** Unit tests 80%+, integration tests for critical paths
- **Test Pyramid:** 70% unit, 25% integration, 5% E2E

## Test Types

**Unit Tests:**
- Framework: pytest + pytest-asyncio
- Location: `tests/unit/<package>/test_<module>.py`
- Mock all external dependencies
- Follow AAA pattern (Arrange, Act, Assert)

**Integration Tests:**
- Scope: API endpoints with real database and Redis
- Location: `tests/integration/`
- Infrastructure: PostgreSQL and Redis in Docker
- GitHub API: Mocked with WireMock

**E2E Tests:**
- Framework: Playwright (future)
- Scope: Critical flows only (auth, card operations)
- Not in MVP CI pipeline

## Continuous Testing

- **CI Integration:** GitHub Actions runs tests on every PR
- **Security Tests:** Bandit (SAST), Dependabot (dependency scanning)

---
