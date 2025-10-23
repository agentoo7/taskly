# Infrastructure and Deployment

## Infrastructure as Code

- **Tool:** Docker Compose + bash deployment scripts
- **Development:** Docker Compose with hot reload
- **Production:** Docker Compose on DigitalOcean Droplets with managed services

## Deployment Strategy

- **Strategy:** Blue-Green Deployment with Health Checks
- **CI/CD Platform:** GitHub Actions
- **Flow:** Push → Tests → Build Image → Deploy Staging → Manual Approval → Deploy Production

## Environments

| Environment | Infrastructure | Purpose |
|-------------|----------------|---------|
| **Development** | Local Docker Compose | Developer machines with hot reload |
| **Staging** | DO Droplet (2vCPU, 4GB) | Pre-production testing |
| **Production** | 2x API Droplets, 2x Celery Droplets, Managed DB/Redis, Load Balancer | Live application |

## Rollback Strategy

- **Primary Method:** Redeploy previous Docker image version
- **Trigger Conditions:** Health check fails, error rate spike, critical bug
- **Recovery Time Objective:** 5 minutes

---
