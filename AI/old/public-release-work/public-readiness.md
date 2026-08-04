# Public Repository Readiness Plan

Goal: make this repository safe enough to publish now, with low overhead for a solo-maintained game project.

Target window: 30-minute practical pass + follow-up improvements later.

## 30-minute solo mode

Status: IN PROGRESS

This is the minimum practical public release pass:

1. Confirm no tracked secrets.
2. Confirm local `.env` is untracked and `.env.example` is safe.
3. Add public-facing repo files: LICENSE, CONTRIBUTING, CODE_OF_CONDUCT.
4. Update root README with setup, test, and docs links.
5. Decide what internal docs stay public and add a short note.

Current pass results:

- Secret scan completed for obvious patterns in repo files.
- `backend/.env` exists locally but is not tracked.
- `backend/.env.example` is using placeholder values.
- Added `LICENSE`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md`.
- Added issue templates under `.github/ISSUE_TEMPLATE/`.
- Root `README.md` updated for public onboarding.

### Public visibility decision for internal docs

Decision: keep `AI/`, `AGENTS.md`, and `HUMANS.md` public.

Rationale: this is a solo game project and these files document how the project was built and tested. They do not contain credentials in the current pass.

Follow-up option: if preferred, move internal workflow notes to a `private-notes` repository later.

## Phase 1: Safety and legal baseline

Status: DONE (minimum pass)

1. Secrets and sensitive data sweep
- Search the full git history and current tree for credentials, tokens, private URLs, and local-only keys.
- Rotate any credential that may have been exposed.
- Replace live values with safe placeholders in sample env files.
- Remove or rewrite local-only defaults that imply production safety.

2. Public visibility review
- Review all files in the AI and HUMANS areas for internal notes that should not be public.
- Decide per file: keep, move to private repo, or rewrite for public context.
- Confirm no private architecture details, infrastructure identifiers, or personal data remain.

3. License and ownership
- Add a top-level license file.
- Confirm third-party assets, icons, and docs are redistributable.
- Add attribution notes where needed.

Deliverable:
- Repo is free of known secrets and has a clear license.

## Phase 2: Contributor-ready documentation

Status: DONE (minimum pass)

1. Rewrite root README for public users
- Add project purpose and current maturity statement.
- Add quick start with one local path using Docker Compose.
- Add testing section with exact commands.
- Add architecture and API doc links.

2. Add contribution docs
- Add CONTRIBUTING guide with branch naming, test expectations, and PR checklist.
- Add issue and PR templates.
- Add CODE_OF_CONDUCT.

3. Clarify support boundaries
- Add known limitations and non-goals.
- Add expected response model for issues and PRs.

Deliverable:
- A first-time contributor can clone, run, test, and open a PR without private guidance.

## Phase 3: Release hygiene and repo policy

Status: IN PROGRESS

1. Git hygiene and ignores
- Keep generated artifacts ignored.
- Keep source, tests, and docs tracked.
- Ensure no local machine files are tracked.

2. Branch protection and CI gate
- Define required checks for pull requests:
  - backend tests
  - frontend unit functional tests
  - frontend user-story E2E tests
- Require passing checks before merge.

3. Versioning and changelog
- Choose semantic versioning policy.
- Add changelog process for release notes.
- Create first tagged baseline release.

Deliverable:
- Public collaboration is guarded by automation and stable release process.

## Phase 4: Final public-release review

Status: IN PROGRESS

1. Dry-run review
- Fresh clone test on a clean machine.
- Full regression run.
- Manual pass of core game flows.

2. Public checklist sign-off
- No secrets
- Clear docs
- CI enforced
- Basic release notes created

3. Visibility switch
- Change repository visibility.
- Publish first release notes and roadmap items.

Deliverable:
- Controlled transition to public visibility.

## Operational checklist (solo practical)

Status: IN PROGRESS

- [x] Secret scan complete for current tree
- [x] Internal docs reviewed and decision recorded
- [x] License added
- [x] README upgraded for external users
- [x] CONTRIBUTING, CODE_OF_CONDUCT, templates added
- [ ] CI required checks enabled (optional for immediate solo release)
- [x] Versioning and changelog process in place
- [x] Final dry run complete (regression suite passed)
- [ ] Repository switched public

## Go-live recommendation for today

Public switch can proceed now if you accept these constraints:

1. CI is not yet enforced in GitHub settings.
2. Deployment hardening is still tracked in the VPS plan and can happen after visibility switch.

Immediate next actions:

1. Push these docs and metadata updates.
2. Switch repository visibility.
3. Add CI required checks when convenient.

## Solo owner note

All items are owner-operated. Keep scope small and prefer shipping with clear docs over over-engineering process.
