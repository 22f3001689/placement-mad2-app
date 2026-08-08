# Research: Backend Jobs

No `[NEEDS CLARIFICATION]` markers remain in spec.md — every open design question (notification
channel, report format, job-status discovery, `User.email`/`EmailTemplate` need) was resolved
directly with the user before/while the spec was written. This document records the resulting
technical decisions made at plan time.

## Decision: Redis runs via Docker, Celery worker/Beat run as plain local processes

**Decision**: A single `docker-compose.yml` at repo root defines one `redis` service
(`redis:7-alpine`, port 6379 published to the host). `make redis-up`/`make redis-down` wrap
`docker compose up -d redis` / `down`. The Celery worker and Beat scheduler are run as regular
`venv/bin/celery` processes (`make celery-worker`, `make celery-beat`), exactly like `flask run`
today — not containerized, so they can import the same Flask app/models/venv directly with no
extra plumbing.

**Rationale**: Redis has no reliable one-command local install path (no system package
available in this dev environment); Docker Engine is available and pulling `redis:7-alpine`
takes seconds. Not containerizing the Python processes keeps debugging identical to every other
process in this project (same venv, same `PYTHONPATH`, same `flask`-style Makefile targets) —
introducing a full docker-compose'd app+worker stack would be a much bigger structural change for
no benefit at this scale.

**Alternatives considered**: Installing Redis from a system package — rejected, not available in
this environment and would tie the setup to one OS's package manager. Running everything
(Flask app, worker, Beat, Redis) in Docker Compose — rejected as premature; this project has no
containerized deployment story at all yet, and adding one just to get Redis running is a much
bigger and riskier change than the milestone calls for.

## Decision: Celery integrates with Flask via a context-aware Task base class

**Decision**: `app/celery_app.py` exposes `make_celery(flask_app)`, following Celery's documented
Flask integration pattern — a custom `Task` subclass whose `__call__` wraps execution in
`flask_app.app_context()`, so every task can use `db.session`, `current_app.config`, etc. exactly
like a request handler. The Celery app's `broker`/`result_backend` both point at the same Redis
instance (`REDIS_URL` env var), and `beat_schedule` is configured in the same module.

**Rationale**: This is Celery's own recommended pattern for Flask apps (avoids needing an
application-context-per-task boilerplate at every call site) and requires no new abstraction
beyond what Celery already documents.

**Alternatives considered**: A separate, from-scratch Flask app instance per task (re-running
`create_app()` inside each task) — rejected as wasteful (re-registers blueprints, re-runs
`db.init_app`, etc. on every task invocation) compared to reusing one long-lived app/context.

## Decision: One `ExportJob` table serves both user-triggered exports and system-generated reports

**Decision**: `ExportJob(id, user_id→User, job_type, status, file_path, period_start,
period_end, created_at, completed_at, error_message)`. `job_type` is `"csv_export"` or
`"placement_report"`. For a placement report, `user_id` is the owning Company's `user_id` (a
Company *is* a User via `Company.user_id`), so report ownership/visibility reuses the exact same
"is this job's `user_id` mine" check as an export — no separate report-ownership code path.

**Rationale**: Both concepts are the same shape end-to-end — an async job owned by one User,
with a status and (once ready) a downloadable file — so one table with a `job_type` discriminator
matches this project's established pattern of app-layer-validated string discriminators (same
approach as `Application.status`, `JobPosition.status`) rather than two near-duplicate tables.

**Alternatives considered**: Separate `CsvExport` and `PlacementReport` tables — rejected as
needless duplication of identical status/ownership/file-path machinery for a difference that's
really just "who/what triggered it," which `job_type` already captures.

## Decision: `Application.interview_reminded_at`, not a separate reminders table

**Decision**: A single nullable `DateTime` column directly on `Application`, set the first time
a reminder is sent for that Application's interview. The recurring reminder job filters on
`interview_reminded_at IS NULL`.

**Rationale**: The spec requires exactly one reminder per Application's interview — a single
timestamp answers "has this been reminded" and "when" in one column, on the row it's already
about. A separate table would only be justified by needing a history of multiple reminders per
Application, which is out of scope.

**Alternatives considered**: A separate `InterviewReminder(application_id, sent_at)` table —
rejected as unnecessary indirection for a 1:1, single-timestamp fact directly describing the
`Application` row it belongs to.

## Decision: `User.email` migration backfills a placeholder for existing rows, enforced as required going forward at the API layer

**Decision**: The Alembic migration adds `email` as a nullable `String` column with a one-time
data-migration step that backfills every existing row with a synthesized placeholder
(`f"{username}@example.invalid"`, guaranteed unique since `username` already is) so the column
can carry a `UNIQUE` index immediately. Registration routes (`register_student`,
`register_company`) then require a real email going forward, validated at the API layer (a
non-empty string containing `@`) — matching this project's established pattern of app-layer
validation over DB-level constraints (same as `Application.status`, `JobPosition.status`).
Admin's email is seeded directly in `data-seeds/seed_data.py`.

**Rationale**: SQLite can't add a `NOT NULL` column with no default to a non-empty table in one
step, and this project's dev database is routinely dropped and reseeded (`make db-seed`) — but
the migration itself still needs to succeed against whatever state a dev DB happens to be in
when it runs, without requiring a reseed first.

**Alternatives considered**: Making the column `nullable=True` forever and only requiring it at
the API layer — rejected because a `UNIQUE` constraint with many `NULL`s is fine in SQLite (NULLs
aren't compared as equal), but leaving it fully optional would mean this milestone's own reminder
job could silently skip real users indefinitely; requiring it going forward is the actual product
intent per the spec's FR-002.

## Decision: EmailTemplate rows are seeded data, matching `Branch`/`Skill`

**Decision**: `EmailTemplate(id, key [unique], subject, body)` where `body`/`subject` contain
Python `str.format()`-style placeholders (e.g. `{student_name}`, `{interview_datetime}`,
`{company_name}`). Three rows are seeded: `interview_reminder`, `export_ready`, `report_ready`.
`app/notifications.py`'s `send_email(to_email, template_key, context)` looks up the row by
`key`, renders both fields with `.format(**context)`, then sends or logs.

**Rationale**: Matches the existing `Branch`/`Skill` master-table pattern (fixed set, seeded, not
user-editable via any UI in this milestone) rather than inventing a new kind of "template" concept
in this codebase.

**Alternatives considered**: Jinja2 templates rendered from files — rejected as unnecessary
power (loops/conditionals) for what's a handful of flat placeholder substitutions; `str.format()`
is already how this project renders its one Jinja file (the SPA shell) and needs no new template
engine dependency for email bodies specifically.
