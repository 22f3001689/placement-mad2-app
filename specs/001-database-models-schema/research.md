# Phase 0 Research: Database Models & Schema

No open `[NEEDS CLARIFICATION]` markers carried over from the spec — the mandated stack (constitution
Principle I) and the sibling reference project resolve every technical unknown below.

## Decision: ORM and migration tool

- **Decision**: Flask-SQLAlchemy for models, Flask-Migrate (Alembic) for schema changes.
- **Rationale**: Mandated by the constitution; `../hms-app-main` already uses this exact combination
  successfully for a structurally similar problem (users with role-specific profile tables, 1:n and n:n
  relationships, cascading history tables).
- **Alternatives considered**: Raw `sqlite3` + hand-written SQL — rejected, since Flask-Migrate gives
  versioned, code-driven schema changes for free and the constitution requires programmatic creation
  anyway; a plain ORM without migrations would make later schema changes (Milestones 2-8) riskier.

## Decision: One `User` table with a role column, not three separate login tables

- **Decision**: Single `User` model (`role` = admin/company/student), with `Company` and `Student` as
  separate 1:1 profile tables keyed by `user_id`.
- **Rationale**: Directly satisfies FR-001/003/004 and mirrors `../hms-app-main`'s
  `User`/`Doctor`/`Patient` split, which solves the identical "one login concept, N profile shapes"
  problem. Keeps auth (Milestone 2) role-agnostic — it only ever queries `User`.
- **Alternatives considered**: Separate `AdminUser`/`CompanyUser`/`StudentUser` tables with no shared
  parent — rejected, it would need three separate login/session code paths, contradicting FR-001 and
  the reused pattern.

## Decision: Enforce "one Application per Student per Job Position" at the schema level

- **Decision**: A composite unique constraint on `(student_id, job_position_id)` in `Application`.
- **Rationale**: FR-007 explicitly requires this be a schema-level guarantee, not just an application-code
  check (which could still race or be bypassed by a future code path). `../hms-app-main`'s
  `DoctorAvailability` model already uses the identical `UniqueConstraint` pattern for a similar
  "no duplicate row for this pair" requirement — directly reusable.
- **Alternatives considered**: Application-layer duplicate check only (`if existing: reject`) — rejected
  as the sole mechanism per FR-007, though it will still be layered on top in the API for a friendlier
  error message once Milestone 5 builds the endpoint.

## Decision: `Placement` is its own table, not just an `Application` status value

- **Decision**: A separate `Placement` model referencing `student_id`, `company_id`, `job_position_id`,
  salary, and joining date, created once an `Application` reaches `Selected`.
- **Rationale**: FR-008 and edge cases require placement history to survive a closed Job Position or a
  deactivated Company — keeping it as only an `Application.status = 'Selected'` value would tie history
  to rows that other milestones might filter out or that reference a closed/deleted parent.
- **Alternatives considered**: Deriving "placed" purely from `Application.status` — rejected because it
  conflates the mutable in-progress application state with the permanent placement record.

## Decision: No automated test suite for this milestone

- **Decision**: Verify manually via seed script + `flask shell`, no pytest.
- **Rationale**: `../hms-app-main` has no test suite despite being a working, submitted course project on
  the same stack; per constitution Principle VII (simplicity), adding a test framework the reference
  project doesn't use would be scope not asked for. Milestone doc's own tracking guidance says "test
  functionality after completing each milestone" — read as manual verification, matching course norms.
- **Alternatives considered**: Introducing `pytest` + `pytest-flask` now — left as an option to revisit
  only if a later milestone or the user explicitly asks for automated tests.
