# VPS Hosting and Deployment Readiness Plan

Goal: make deployment on a single fixed-cost VPS predictable and low-maintenance, while preserving the existing local Docker workflow.

Target window: 7 to 14 working days.

## Deployment model

Primary target:
- One Linux VPS
- Docker Engine with Docker Compose plugin
- Reverse proxy with automatic HTTPS
- PostgreSQL in a Docker volume

Principles:
- Keep local development Compose separate from production Compose.
- Avoid host-level manual steps except initial bootstrap.
- Make rollback as simple as selecting a previous image tag.

## Phase 1: Production Compose baseline (Day 1-3)

Status: TODO

1. Add production compose file
- Create docker-compose.prod.yml with no bind mounts.
- Use prebuilt images or deterministic Docker builds.
- Remove dev server commands and use production start commands.

2. Service hardening
- Add restart policies.
- Add healthchecks for backend and frontend.
- Use named volumes for database persistence.

3. Environment split
- Define separate env files for dev and prod.
- Document required variables with safe defaults only in examples.

Deliverable:
- A production-focused compose stack that can boot on a clean VPS.

## Phase 2: Runtime reliability and observability (Day 3-6)

Status: TODO

1. Reverse proxy and TLS
- Add reverse proxy service (Caddy or Nginx) in production compose.
- Route domain traffic to frontend and API.
- Automate certificate issuance and renewal.

2. Logging and monitoring
- Configure container log limits.
- Add basic health endpoint checks.
- Document where to inspect logs and service status.

3. Backup and restore baseline
- Add scheduled PostgreSQL backup script.
- Document restore procedure and test it.

Deliverable:
- Minimum viable operational reliability for a single-node deployment.

## Phase 3: Deployment workflow (Day 6-9)

Status: TODO

1. Build and release flow
- Define image tags by commit SHA and release version.
- Document push path to container registry.

2. Deploy and rollback commands
- Add deploy script:
  - pull images
  - run migrations
  - start services
  - verify health
- Add rollback script:
  - switch to previous image tag
  - restart services

3. Database migration safety
- Ensure migrations run before app traffic cutover.
- Document rollback caveats for schema-changing releases.

Deliverable:
- Repeatable deploy and rollback process with clear operator steps.

## Phase 4: Hardened handoff docs (Day 9-14)

Status: TODO

1. Create operator runbook
- New server bootstrap
- DNS and domain setup
- Initial deploy
- Routine updates
- Incident response basics

2. Add release checklists
- Pre-deploy checks
- Post-deploy checks
- Weekly maintenance checks

3. Perform test deployment
- Provision a fresh VPS.
- Execute runbook exactly.
- Fix gaps found during trial.

Deliverable:
- A tested runbook another maintainer can execute without tribal knowledge.

## Required production artifacts

Status: TODO

- [ ] docker-compose.prod.yml
- [ ] backend production entrypoint or command profile
- [ ] frontend production runtime config
- [ ] reverse proxy config
- [ ] env template for production
- [ ] deploy script
- [ ] rollback script
- [ ] backup and restore scripts
- [ ] VPS runbook

## Recommended deployment sequence after repo is public

1. Finalize public-readiness work.
2. Implement production compose and runtime hardening.
3. Stand up a staging VPS and run full regression.
4. Cut first production release from a signed tag.
5. Monitor for one week before feature-scale expansion.
