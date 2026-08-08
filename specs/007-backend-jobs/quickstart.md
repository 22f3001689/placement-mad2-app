# Quickstart: Backend Jobs

## One-time local setup

1. `make redis-up` — starts a local Redis container (`docker compose up -d redis`).
2. Copy `.env.example` to `.env` and fill in `REDIS_URL` (default `redis://localhost:6379/0`
   works with step 1 as-is) and, optionally, the Mailtrap `MAIL_*` values if you want to see
   real emails arrive in the Mailtrap sandbox inbox. Leave `MAIL_*` unset to use the log
   fallback instead.
3. `flask db upgrade` (picks up this milestone's migrations), `make db-seed`.
4. In separate terminals: `flask run`, `make celery-worker`, `make celery-beat`.

## Scenario 1: interview reminder email (US1)

1. As a Company, schedule an interview on an Application with a datetime a few minutes in the
   future (so the reminder's lookahead window catches it without waiting a full day).
2. Either wait for Celery Beat's next tick, or manually invoke the reminder task once
   (`flask shell` → `from app.tasks import send_interview_reminders; send_interview_reminders()`).
3. Confirm: if `MAIL_*` is configured, the email appears in the Mailtrap inbox; otherwise, the
   rendered subject/body appear in the Celery worker's log output.
4. Re-run the task again without changing anything — confirm no second reminder is sent
   (`Application.interview_reminded_at` is now set).

## Scenario 2: Student/Company CSV export (US2)

1. As a Student (or Company), `POST /api/student/exports` (or `/api/company/exports`) — confirm
   an immediate `202` with `status="pending"`, not a hang.
2. Poll `GET /api/student/exports/<id>` until `status="ready"`.
3. Download the file at its `download_url` — confirm it contains only that Student's own
   applications (or that Company's own applications/placements), and that the configured
   notification channel received a completion alert.
4. As a different Student/Company, confirm `GET /student/exports/<id>` (or the company
   equivalent) for someone else's job id returns `404`.

## Scenario 3: periodic placement report (US3)

1. Ensure at least one Company has applications/placements recorded.
2. Manually invoke the report task once (`flask shell` →
   `from app.tasks import generate_placement_reports; generate_placement_reports()`).
3. As that Company, `GET /company/reports` — confirm a new report appears with a working
   `download_url`, and its content matches that Company's own application/placement counts for
   the covered period.
4. As a Company with no drives/applications at all, confirm no report was generated for it.
5. Re-run the task again immediately — confirm no duplicate report is generated for the same
   period.

## Verifying graceful degradation

Stop the Redis container (`make redis-down`) and confirm: `POST /api/student/exports` now
responds `503` immediately (no hang), while every pre-existing endpoint (login, drives,
applications, etc.) continues to work normally.
