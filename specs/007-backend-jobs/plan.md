# Implementation Plan: Backend Jobs — Interview Reminders, Placement Reports, and Triggered Exports

**Branch**: `007-backend-jobs` | **Date**: 2026-08-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-backend-jobs/spec.md`

## Summary

Introduce this app's first background-job infrastructure (Celery + Redis, both mandated by
the constitution but unused until now) to run: a Celery Beat job that emails Students an
interview reminder exactly once per upcoming interview; a Celery Beat job that generates a
per-Company HTML placement/application report each reporting period; and a user-triggered,
Celery-executed CSV export (Student's own applications, or a Company's own
applications/placements) that the frontend polls for completion. Emails are rendered from a
new `EmailTemplate` table and sent via SMTP (Mailtrap sandbox in local dev), falling back to
a log line when no SMTP server is configured. Redis runs locally via Docker (no system
package install required); Celery worker/beat run as plain local Python processes, same as
`flask run`.

## Technical Context

**Language/Version**: Python 3.11 (Flask + Celery), JavaScript (Vue 3) — same as prior milestones

**Primary Dependencies**: `celery[redis]`, `redis` (client), `python-dotenv` (new); Flask/Flask-SQLAlchemy/Flask-Migrate/Flask-Login (existing)

**Storage**: SQLite via SQLAlchemy (unchanged) for all relational data; Redis as Celery's broker and result backend (new); generated files (CSV exports, HTML reports) written to `app/static/exports/` and `app/static/reports/`, served via the existing `static_url()` pattern — no new storage technology

**Testing**: Manual verification via `curl`/browser plus direct Celery task invocation (`task.apply()` synchronously) against the running app, per this project's established no-automated-suite convention

**Target Platform**: Same Linux dev container as always; Redis runs in a local Docker container (Docker Engine required on the dev machine, not a cloud service)

**Project Type**: Web application (existing `app/` + `frontend/` structure) + new background-worker process

**Performance Goals**: N/A — demo-scale data volumes

**Constraints**: Every new job MUST be idempotent against duplicate/overlapping Beat ticks (no double reminders, no double reports for the same period); SMTP credentials MUST never be committed (`.env`, gitignored, `.env.example` placeholders only); the app MUST keep working with Redis/Celery down (only the new background-job endpoints fail, nothing pre-existing breaks)

**Scale/Scope**: 1 new Alembic migration set (User.email, Application.interview_reminded_at, EmailTemplate, ExportJob), 1 new Celery app module, 1 new tasks module, 1 new notifications module, ~6 new routes across `student.py`/`company.py`, 1 `docker-compose.yml`, `Makefile` additions, no new Vue views (existing dashboards gain a small export/report section each)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Mandated stack (Redis, Redis+Celery)**: PASS — this milestone is the first to actually use the Redis+Celery slice of the mandated stack; Docker is used only as a local run-mechanism for the Redis *server* (no system package needed), not a framework substitution — Redis itself remains the broker/backend.
- **Programmatic DB creation, migrations only**: PASS — `User.email`, `Application.interview_reminded_at`, `EmailTemplate`, `ExportJob` all ship as Alembic migrations.
- **Role-based access, ownership checks**: PASS — export/report status and download endpoints re-check ownership (Student sees only their own export; Company sees only its own exports/reports) using the same 404-not-403 convention as existing endpoints.
- **Local-demo-first, mockable notification channel**: PASS — no SMTP configured → email content is logged instead of sent; Redis is local Docker, not a cloud dependency; app functions for all pre-existing features even if Redis/Celery aren't running.
- **Reuse before rebuild**: PASS — downloadable files reuse the existing `static_url()`/`app/static/` serving pattern (same as resume/photo/logo) rather than inventing a new download endpoint; `../hms-app-main` has no Celery/Redis/mail precedent to reuse from (confirmed by inspection), so this part is genuinely new.
- **Specs/plans name the exact mechanism**: PASS — this plan names Celery Beat, Redis (Docker-run), SMTP via `smtplib`, and the exact new tables below.

No violations; Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/007-backend-jobs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── student-api.md
│   └── company-api.md
└── tasks.md              # /speckit-tasks output, not created here
```

### Source Code (repository root)

```text
app/
├── celery_app.py              # new: Celery app factory, Flask-context-aware task base
├── tasks.py                   # new: send_interview_reminders, generate_placement_reports,
│                                #      process_export_job (Beat + user-triggered tasks)
├── notifications.py            # new: send_email(to, template_key, context) - SMTP or log fallback
├── models.py                   # + User.email, Application.interview_reminded_at,
│                                #   EmailTemplate, ExportJob
├── routes/
│   ├── student.py               # + POST/GET /student/exports[, /<id>]
│   └── company.py               # + POST/GET /company/exports[, /<id>], GET /company/reports
migrations/versions/
├── <new>_add_user_email.py
├── <new>_add_interview_reminded_at.py
└── <new>_add_email_template_and_export_job.py

data-seeds/seed_data.py         # + seed EmailTemplate rows, seed User.email for the 3 accounts

docker-compose.yml               # new: single `redis` service (also reused by Milestone 8's caching)
.env.example                     # new: REDIS_URL, MAIL_* placeholders (no real values)
requirements.txt                 # + celery[redis], redis, python-dotenv
Makefile                         # + redis-up/redis-down, celery-worker, celery-beat targets
```

**Structure Decision**: Existing single Flask app + single Vue SPA structure, extended with a
background-worker process (Celery) that imports the same Flask app/models — no new backend
service, no new frontend app. Export/report endpoints live in the existing per-role blueprints
(`student.py`, `company.py`), matching how every other capability in this app is organized.

## Complexity Tracking

Not applicable — no Constitution Check violations.
