# Introduction

This document outlines the overall project architecture for **Taskly**, including backend systems, shared services, and non-UI specific concerns. Its primary goal is to serve as the guiding architectural blueprint for AI-driven development, ensuring consistency and adherence to chosen patterns and technologies.

**Relationship to Frontend Architecture:**
If the project includes a significant user interface, a separate Frontend Architecture Document will detail the frontend-specific design and MUST be used in conjunction with this document. Core technology stack choices documented herein (see "Tech Stack") are definitive for the entire project, including any frontend components.

## Starter Template Decision

**Backend (FastAPI):** No starter template - manual setup from scratch
- Rationale: FastAPI is minimal by design; PRD specifies custom architecture (async SQLAlchemy 2.0, Celery, FastAPI WebSockets). Manual setup gives full control without unnecessary boilerplate.

**Frontend:** Deferred to separate Frontend Architecture Document (out of scope for backend architecture)

**Monorepo:** npm workspaces (simple, built-in, sufficient for MVP)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-23 | 1.0 | Initial backend architecture draft | Winston (Architect Agent) |

---
