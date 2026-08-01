# Implementation Plan: Admin Dashboard & Management

**Branch**: `docs/milestone-3-redesign` | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-admin-dashboard-management/spec.md`

## Summary

Build a single-page Admin dashboard: one Vue view with a welcome/search header (Section 1) and five
subsections (Section 2) — Registered Companies, Registered Students, Company Applications, Ongoing
Drives, Student Applications. Backed by a JSON API under `/api/admin`, gated end-to-end by the
existing `role_required("admin")` decorator from Milestone 2. `JobPosition.status` ("Drive") drops the
Milestone-1-anticipated approval workflow in favor of a simple `ongoing`/`completed` lifecycle, per the
business-flow clarification in spec.md.

## Technical Context

**Language/Version**: Python 3.11 (backend, unchanged); Node 20 LTS + npm (frontend build tooling
only, unchanged).

**Primary Dependencies**: Flask, Flask-Login, Flask-SQLAlchemy, Flask-Migrate (all existing). SQLAlchemy's
`or_`/`ilike` for search, same as before. Frontend: Vue 3 (existing) — no new dependency. Modals are a
small hand-rolled `Modal.vue` component styled with existing Bootstrap CSS classes (`.modal`,
`.modal-dialog`, `.modal-content`), toggled with plain `v-if` — deliberately not pulling in Bootstrap's
JS bundle just for two read-only popups.

**Storage**: SQLite, unchanged. No schema migration — `JobPosition.status`'s *meaning* changes (see
spec.md Key Entities) but it's still a plain string column; only the Python-side default value and the
values the app writes into it change.

**Testing**: No automated test suite — same decision as Milestones 1-2; verified manually via
`quickstart.md`.

**Target Platform**: Local developer machine, same two run modes as before.

**Project Type**: Web application (unchanged).

**Performance Goals**: N/A.

**Constraints**: Bootstrap CSS only, no Bootstrap JS bundle (see Primary Dependencies); Jinja stays a
single entry shell.

**Scale/Scope**: 7 API endpoints under `/api/admin` (one fewer than the original draft — Job Posting
approve/reject is dropped, replaced by one "mark complete" endpoint), 1 single-page Vue view replacing
both the Milestone 2 `AdminHome.vue` placeholder and the original draft's 4 separate sub-pages, 1 small
reusable `Modal.vue`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Mandated Stack | Flask + Vue + Bootstrap (CDN, CSS only) + SQLite unchanged; no new dependency | PASS |
| II. Programmatic DB Creation | No schema/migration change — same column, same type, different string values written into it | PASS |
| III. Role-Based Access | Every endpoint wrapped in the existing `role_required("admin")` decorator | PASS |
| IV. Reuse Before Rebuild | Search still follows `../hms-app-main/app/routes/admin.py`'s `or_`/`ilike` pattern; blacklist/whitelist reuses its `is_blacklisted`-toggle pattern verbatim (mapped to this project's `is_active`) | PASS |
| V. Local-Demo-First | No new external service, no CORS change | PASS |
| VI. Milestone-Sliced | This plan covers Milestone 3 only — Company/Student self-service dashboards stay out of scope (Milestones 4-5); Ongoing Drives is verified here with a directly-seeded Drive since Milestone 4's create-Drive endpoint doesn't exist yet | PASS |
| VII. Simple/Human/Surgical | One single-page view instead of a router tree of sub-pages — matches the actual requested UI and removes 4 route entries + 4 separate view files from the original draft; one toggle endpoint (not two) for blacklist/whitelist, one decision endpoint (not two) for Company approve/reject | PASS |

No new complexity to justify.

## Project Structure

### Documentation (this feature)

```text
specs/003-admin-dashboard-management/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── contracts/
│   └── admin-api.md      # Phase 1 output - the 7 endpoints
└── quickstart.md         # Phase 1 output
```

No `data-model.md`: no new entities or columns.

### Source Code (repository root)

```text
app/
├── models.py                 # JobPosition.status default changes "pending" -> "ongoing"
├── routes/
│   └── admin.py                # 7 endpoints (see contracts/admin-api.md)
data-seeds/
└── seed_data.py                 # sample JobPosition seeded with status="ongoing"
frontend/src/
├── router/index.js               # /admin is now the only Admin route (sub-routes removed)
├── components/
│   └── Modal.vue                   # NEW: small reusable read-only modal
└── views/
    └── AdminHome.vue                 # REPLACES the Milestone 2 ping placeholder AND the
                                       # original 4-sub-page draft with one single-page dashboard
```

**Structure Decision**: Collapses back to one view file (`AdminHome.vue`) instead of the original
draft's four separate views + four router entries — the actual requested design is a single page, so
that's what the structure now reflects. One new `frontend/src/components/` directory for the shared
`Modal.vue`, since two of the five subsections need one.

## Complexity Tracking

*No violations — table intentionally omitted.*
