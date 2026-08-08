# Implementation Plan: Job Application History and Status Tracking

**Branch**: `006-application-history-status` | **Date**: 2026-08-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-application-history-status/spec.md`

## Summary

Replace the current 5-value `Application.status` vocabulary with the milestone's 6-value
one (Applied/Shortlisted/Interview/Offer/Rejected/Placed), make Placed a terminal status
that auto-creates the `Placement` row it currently never creates outside seed data, close
the live-approval gap so Students never see/apply to drives from a since-unapproved
Company, and give Admin/Company a full Student-profile view. All changes are additive to
the existing Flask blueprints/Vue views from Milestones 1-5 — no new services, no new
storage technology.

## Technical Context

**Language/Version**: Python 3.11 (Flask), JavaScript (Vue 3, Vite) — same as all prior milestones

**Primary Dependencies**: Flask, Flask-SQLAlchemy, Flask-Migrate/Alembic, Flask-Login (backend); Vue 3, Vue Router (frontend) — no new dependencies

**Storage**: SQLite via SQLAlchemy — one Alembic migration for the status-vocabulary data change; no new tables

**Testing**: Manual verification via `curl`/browser against the running dev server, per this project's established pattern (no automated test suite in this repo)

**Target Platform**: Same-origin web app, Linux server (dev container), browser client

**Project Type**: Web application (Flask backend + Vue SPA), existing `app/` + `frontend/` structure

**Performance Goals**: N/A — demo-scale data volumes, no specific performance target

**Constraints**: SQLite batch-alter migrations must name constraints explicitly (established Milestone-5 gotcha); status changes must be atomic with Placement creation (single DB transaction)

**Scale/Scope**: 3 backend route files touched (admin, company, student), 1 model file, 1 migration, 3 Vue views touched (AdminHome, CompanyHome, StudentHome) — no new files beyond the migration and this spec's docs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Flask+Vue+SQLite stack, no new tech** (Principle-implied via Tech Stack mandate): PASS — no new dependency introduced.
- **Schema changes only via Alembic migration, never hand-edited `.db`**: PASS — one migration authored for the status-vocabulary data rewrite; no manual `.db` edits.
- **Role-based access via existing `User.role` discriminator / decorators**: PASS — reuses `role_required`/`company_approved_required`, no new auth mechanism.
- **Simple/Human/Surgical code**: PASS — status-vocabulary change is a rename + one new terminal-state guard + one new Placement-creation side effect; no speculative abstraction introduced.
- **Milestone-sliced delivery, spec reviewed before implementation**: PASS — this plan follows the already-reviewed and merged spec.md.

No violations; Complexity Tracking table is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/006-application-history-status/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/
│   ├── company-api.md
│   ├── student-api.md
│   └── admin-api.md
└── tasks.md              # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
app/
├── models.py                 # Application: no schema change, only valid status values change
├── routes/
│   ├── admin.py               # + GET /admin/students/<id> (full profile + history)
│   ├── company.py             # decide_application: new status vocab, terminal guard, Placed→Placement
│   └── student.py             # list_drives/get_drive/apply_to_drive: live Company-approval gate
migrations/versions/
└── <new>_migrate_application_status_vocabulary.py

frontend/src/views/
├── AdminHome.vue              # Registered Students: + "View Profile" → new profile/history modal
├── CompanyHome.vue            # Status dropdown: 6 new values; Placed prompts for position/salary/joining date
└── StudentHome.vue            # History modal: + placement outcome row when Placed
```

**Structure Decision**: Existing single Flask app + single Vue SPA structure (unchanged since
Milestone 1). This feature is a data/behavior change layered onto existing blueprints and
views, not a new module.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

Not applicable — no Constitution Check violations.
