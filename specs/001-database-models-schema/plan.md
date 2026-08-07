# Implementation Plan: Database Models & Schema

**Branch**: `docs/milestone-1-plan` | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-database-models-schema/spec.md`

## Summary

Build the SQLAlchemy models for User (Admin/Company/Student), Company profile, Student profile, Job
Position (Placement Drive), Application, and Placement, wired together with the relationships and
constraints the spec calls for, plus a seed script that guarantees exactly one Admin. This is a schema-only
milestone: no routes, no auth, no Vue — just `app/models.py`, a migration, and a seed script, laid out the
same way as the sibling `../hms-app-main` project.

## Technical Context

**Language/Version**: Python 3.11 (matches `../hms-app-main`)

**Primary Dependencies**: Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login (`UserMixin` on `User` now,
even though login itself is Milestone 2 — cheap to add alongside the model and avoids touching this file
again next milestone), Werkzeug (`generate_password_hash`/`check_password_hash`)

**Storage**: SQLite, file at `app.db` in repo root (mandated stack; created via `flask db upgrade`, never
by hand)

**Testing**: No pytest suite — matching `../hms-app-main`, which has none either. Verification is manual:
run the seed script against a clean database and inspect the result via `flask shell` (see quickstart.md).
This keeps the milestone to what was actually asked for (Principle VII, simplicity) rather than introducing
a test framework the reference project doesn't use.

**Target Platform**: Local developer machine (Linux/macOS), demoed locally per constitution Principle V

**Project Type**: Web application (Flask API backend now; Vue frontend arrives in a later milestone)

**Performance Goals**: N/A for this milestone — no endpoints exist yet

**Constraints**: SQLite only; schema via code only (models + Flask-Migrate migrations); exactly one Admin

**Scale/Scope**: 6 models, ~5 relationships, 1 seed script. Single-institute scale (tens of companies,
hundreds of students) — no sharding/partitioning concerns.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Mandated Stack | Flask + SQLAlchemy + SQLite + Flask-Migrate only; no other DB/ORM | PASS |
| II. Programmatic DB Creation | Models + `flask db migrate/upgrade` + seed script; no manual `.db` editing | PASS |
| III. Role-Based Access | Single `User` model with `role` column (admin/company/student) | PASS |
| IV. Reuse Before Rebuild | Directly reuses `../hms-app-main`'s `app/` layout, `User`/profile split, `config.py`, seed-script pattern | PASS |
| V. Local-Demo-First | SQLite file, no cloud dependency | PASS |
| VI. Milestone-Sliced | This plan covers Milestone 1 only; no auth/routes/UI included | PASS |
| VII. Simple/Human/Surgical | No test framework added since the reused reference project has none; no speculative fields beyond what spec/milestone docs list | PASS |

No violations. Complexity Tracking section omitted (nothing to justify).

## Project Structure

### Documentation (this feature)

```text
specs/001-database-models-schema/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
└── quickstart.md         # Phase 1 output
```

No `contracts/` directory: this milestone exposes no API — it is schema only.

### Source Code (repository root)

```text
app/
├── __init__.py           # create_app(); db, login, migrate extension objects (copy hms-app-main pattern)
├── models.py              # User, Company, Student, JobPosition, Application, Placement
└── routes/                # created empty/untouched here; populated starting Milestone 2

config.py                  # Config class: SECRET_KEY, SQLALCHEMY_DATABASE_URI (sqlite:///app.db), etc.
migrations/                 # Flask-Migrate output (flask db init/migrate/upgrade)
data-seeds/
└── seed_data.py            # Creates the one Admin + a handful of sample companies/students for local demo
```

**Structure Decision**: Mirror `../hms-app-main` exactly at the repo root (`app/`, `config.py`,
`migrations/`, `data-seeds/`) rather than a `backend/` subfolder — the Flask app owns the repo root, and the
Vue frontend (added in a later milestone) will live in its own top-level `frontend/` directory alongside it,
same as any Flask+Vue split project. This keeps Milestone 1 a pure copy-and-adapt of a working pattern
rather than a new layout to design.

## Complexity Tracking

*No violations — table omitted.*
