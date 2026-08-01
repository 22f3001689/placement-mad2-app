# Implementation Plan: Admin Dashboard & Management

**Branch**: `docs/milestone-3-plan` | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-admin-dashboard-management/spec.md`

## Summary

Add a JSON admin API (dashboard totals, Company list/search/approve-reject, Student search, Job
Posting list/approve-reject, Application listing, account deactivate/reactivate toggle) on top of
Milestone 1's models, gated end-to-end by the existing `role_required("admin")` decorator from
Milestone 2. On the frontend, replace the `AdminHome.vue` placeholder with a real dashboard view plus
small sub-views for each management action, all built on the same `api/http.js` fetch wrapper and
`state/auth.js` session already in place.

## Technical Context

**Language/Version**: Python 3.11 (backend, unchanged); Node 20 LTS + npm (frontend build tooling
only, unchanged from Milestone 2).

**Primary Dependencies**: Flask, Flask-Login, Flask-SQLAlchemy, Flask-Migrate (all existing, no new
backend dependency). SQLAlchemy's `or_`/`ilike` for substring search — the same pattern
`../hms-app-main/app/routes/admin.py` already uses for its doctor/patient search, adapted from Jinja
forms to JSON responses. Frontend: Vue 3, Vue Router (existing) — no new frontend dependency.

**Storage**: SQLite, unchanged. No schema migration needed — `Company.approval_status` and
`JobPosition.status` already accept arbitrary strings; this milestone is the first to write
`"rejected"` into them. `User.is_active` already exists and is already enforced at login (Milestone 2).

**Testing**: No automated test suite — same decision as Milestones 1-2
(`../001-database-models-schema/research.md`); verified manually via `quickstart.md`.

**Target Platform**: Local developer machine, same two run modes as Milestone 2 (Vite dev server +
Flask, or built bundle served by Flask alone).

**Project Type**: Web application (unchanged).

**Performance Goals**: N/A — no load targets stated for this milestone.

**Constraints**: Bootstrap only for styling; Jinja stays a single entry shell (constitution Principle
I, unchanged).

**Scale/Scope**: 8 new API endpoints under `/api/admin`, 1 real dashboard view replacing the
`AdminHome.vue` placeholder, ~4 small Vue sub-views (Companies, Students, Job Postings, Applications).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Mandated Stack | Flask + Vue + Bootstrap (CDN) + SQLite unchanged; no new dependency of any kind | PASS |
| II. Programmatic DB Creation | No schema/migration change — reuses existing columns, only writes new string values into them | PASS |
| III. Role-Based Access | Every new endpoint wrapped in the existing `role_required("admin")` decorator — no new access-control mechanism | PASS |
| IV. Reuse Before Rebuild | Search (`or_`/`ilike`) and the active/inactive toggle both follow `../hms-app-main/app/routes/admin.py`'s search and blacklist-toggle patterns, adapted from Jinja+flash to JSON | PASS |
| V. Local-Demo-First | No new external service, no CORS change | PASS |
| VI. Milestone-Sliced | This plan covers Milestone 3 only — Company/Student self-service dashboards stay out of scope (Milestones 4-5) | PASS |
| VII. Simple/Human/Surgical | Approve/reject reuses a single generic "decision" endpoint per entity (body carries the target status) rather than separate approve/reject routes, and deactivate/reactivate is one toggle endpoint, not two — smaller surface, same capability | PASS |

No new complexity to justify — this milestone adds routes and views, not new abstractions.

## Project Structure

### Documentation (this feature)

```text
specs/003-admin-dashboard-management/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── contracts/
│   └── admin-api.md      # Phase 1 output - the 8 endpoints
└── quickstart.md         # Phase 1 output
```

No `data-model.md`: no new entities or columns (spec.md's Key Entities section says so explicitly).

### Source Code (repository root)

```text
app/
├── routes/
│   └── admin.py            # REPLACES the Milestone 2 /ping placeholder with 8 real endpoints
frontend/src/
├── views/
│   ├── AdminHome.vue         # REPLACED: real dashboard totals + links to the 4 sub-views below
│   ├── AdminCompanies.vue     # NEW: list/search/approve/reject Companies
│   ├── AdminStudents.vue      # NEW: list/search Students, deactivate/reactivate
│   ├── AdminJobPostings.vue   # NEW: list/search Job Postings, approve/reject
│   └── AdminApplications.vue  # NEW: list all Applications
└── router/index.js            # + 4 child routes under /admin, still guarded by meta.role="admin"
```

**Structure Decision**: Everything lives inside the existing `app/routes/admin.py` blueprint and the
existing `/admin` frontend route tree — this milestone is additive within structure Milestone 2 already
established, no new top-level directories.

## Complexity Tracking

*No violations — table intentionally omitted.*
