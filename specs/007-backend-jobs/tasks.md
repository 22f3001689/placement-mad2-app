# Tasks: Backend Jobs — Interview Reminders, Placement Reports, and Triggered Exports

**Input**: Design documents from `/specs/007-backend-jobs/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not requested for this milestone (project convention: manual verification via quickstart.md).

**Organization**: Tasks are grouped by user story (US1-US3, per spec.md).

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [X] T001 Confirm Docker Engine is available locally (`docker --version`, `docker compose version`); confirm on branch `feat/milestone-7-backend-jobs` off latest `main`
- [X] T002 Add `celery[redis]`, `redis`, and `python-dotenv` to `requirements.txt`; `pip install -r requirements.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infrastructure every user story depends on — Redis running, Celery wired to Flask, schema in place, secrets loaded.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Create `docker-compose.yml` at repo root with a single `redis` service (`redis:7-alpine`, port `6379:6379`)
- [X] T004 [P] Add `redis-up`/`redis-down` targets to `Makefile` (`docker compose up -d redis` / `down`), and `celery-worker`/`celery-beat` targets (`venv/bin/celery -A app.celery_app worker --loglevel=info` / `... beat --loglevel=info`)
- [X] T005 [P] Create `.env.example` documenting `REDIS_URL`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_USE_TLS`, `MAIL_DEFAULT_SENDER` with placeholder values only (no real credentials); confirm `.env`/`.env.*` (except `.env.example`) are already gitignored
- [X] T006 In `config.py`, call `load_dotenv()` (from `python-dotenv`) before the `Config` class, and add `REDIS_URL`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_USE_TLS`, `MAIL_DEFAULT_SENDER` as `os.environ.get(...)`-backed class attributes (all optional/`None`-able except `REDIS_URL`, which defaults to `redis://localhost:6379/0`)
- [X] T007 Create `app/celery_app.py`: `make_celery(flask_app)` factory using Celery's documented Flask-context `Task` subclass pattern (per research.md), broker/result_backend from `Config.REDIS_URL`, and an empty `beat_schedule` dict (populated in later phases); instantiate the Celery app at module level via `from app import create_app; celery = make_celery(create_app())` so `celery -A app.celery_app` works
- [X] T008 [P] Add to `app/constants.py`: `EXPORT_JOB_TYPE_CSV_EXPORT = "csv_export"`, `EXPORT_JOB_TYPE_PLACEMENT_REPORT = "placement_report"`, `EXPORT_JOB_STATUSES = ("pending", "running", "ready", "failed")` with named `EXPORT_JOB_STATUS_PENDING/RUNNING/READY/FAILED` constants
- [X] T009 In `app/models.py`: add `User.email` (`String(255)`, `unique=True`, `nullable=True`), `Application.interview_reminded_at` (`DateTime`, `nullable=True`), new `EmailTemplate` model (`id`, `key` unique, `subject`, `body`), new `ExportJob` model (`id`, `user_id`→`User`, `job_type`, `status` default `EXPORT_JOB_STATUS_PENDING`, `file_path`, `period_start`, `period_end`, `error_message`, `created_at`, `completed_at`)
- [X] T010 Author and apply the three migrations (per data-model.md/research.md): (a) add `users.email` + one-time backfill of `f"{username}@example.invalid"` for existing rows + unique index; (b) add `application.interview_reminded_at`; (c) create `email_template` and `export_job` tables
- [X] T011 [P] Create `app/notifications.py`: `send_email(to_email, template_key, context)` — looks up `EmailTemplate` by `key`, renders `subject`/`body` via `.format(**context)`, sends via `smtplib.SMTP` using `Config.MAIL_*` if `MAIL_SERVER` is set, otherwise logs the rendered subject/body via `get_logger(__name__)`; catches and logs any SMTP exception rather than raising (per spec Edge Cases)
- [X] T012 In `data-seeds/seed_data.py`: seed the three `EmailTemplate` rows (`interview_reminder`, `export_ready`, `report_ready`, per data-model.md's placeholder lists) and set a real `email` for the three seeded accounts (admin/company/student)
- [X] T013 Run `flask db upgrade`, `make db-seed`, `make redis-up`, and verify `python3 -c "from app.celery_app import celery; print(celery)"` succeeds with no errors

**Checkpoint**: Redis is running locally, Celery app is importable, schema has `User.email`/`Application.interview_reminded_at`/`EmailTemplate`/`ExportJob`, and `send_email()` works (logs, since no `MAIL_*` is set yet).

---

## Phase 3: User Story 1 - Student gets reminded of an upcoming interview automatically (Priority: P1) 🎯 MVP

**Goal**: A Celery Beat job emails (or logs, if unconfigured) exactly one reminder per Application with an upcoming, not-yet-reminded interview.

**Independent Test**: Schedule a near-future interview, trigger the reminder task, confirm exactly one reminder is delivered/logged and re-running the task sends no duplicate.

### Implementation for User Story 1

- [X] T014 [US1] Create `app/tasks.py`; add `send_interview_reminders()`: query `Application` where `interview_datetime` is between now and a fixed lookahead window (e.g. next 24h), `interview_reminded_at IS NULL`, and `status` not in `TERMINAL_APPLICATION_STATUSES`; for each, call `send_email(student.email, "interview_reminder", {...})` and set `interview_reminded_at = utcnow()`, committing per-Application (so one failure doesn't block the rest)
- [X] T015 [US1] Register `send_interview_reminders` in `app/celery_app.py`'s `beat_schedule` (e.g. every 15 minutes) and decorate it as a Celery task (`@celery.task`)
- [X] T016 [US1] In `app/routes/auth.py`, require and validate `email` (non-empty, contains `@`) in `register_student` and `register_company`, storing it on the new `User.email` column
- [X] T017 [US1] Add an `email` `<input type="email" required>` field to `frontend/src/views/RegisterStudent.vue` and `RegisterCompany.vue`, submitted alongside username/password
- [X] T018 [US1] Manually verify via quickstart.md Scenario 1 (schedule interview, trigger task, confirm single delivery, confirm no duplicate on re-run, confirm skip-if-terminal-status and skip-if-already-passed edge cases)

**Checkpoint**: User Story 1 is fully functional and independently testable — this alone proves Celery Beat + email delivery/log-fallback work end-to-end.

---

## Phase 4: User Story 2 - Student or Company exports their own history as CSV without blocking the UI (Priority: P1)

**Goal**: A Student/Company can request an async CSV export, poll its status, and download it once ready, scoped strictly to their own data.

**Independent Test**: Request an export, confirm immediate response, poll to `ready`, download, confirm rows belong only to the requester, confirm a completion alert was sent/logged.

### Implementation for User Story 2

- [X] T019 [US2] In `app/tasks.py`, add `process_export_job(job_id)` (`@celery.task`): loads the `ExportJob`, sets `status=running`, dispatches on `job_type` (this phase implements the `csv_export` branch: writes a CSV to `app/static/exports/` containing the owning User's own applications — or, for a Company `user_id`, that Company's own applications/placements), sets `status=ready`, `file_path`, `completed_at`, and calls `send_email(owner.email, "export_ready", {...})`; wraps the body in try/except, setting `status=failed`/`error_message` on any exception instead of letting the task crash silently
- [X] T020 [US2] In `app/routes/student.py`, add `POST /student/exports` (creates an `ExportJob(job_type=csv_export, user_id=current_user.id)`, calls `process_export_job.delay(job.id)`, returns `202`; catches broker-connection errors and returns `503` per contracts/student-api.md), `GET /student/exports`, and `GET /student/exports/<id>` (404 if not owned)
- [X] T021 [P] [US2] In `app/routes/company.py`, add the same three endpoints under `/company/exports`, scoped to `current_user.company_profile`'s own applications/placements, per contracts/company-api.md
- [X] T022 [P] [US2] Add a small "Export My Applications" button + status poll + download link to `frontend/src/views/StudentHome.vue`
- [X] T023 [P] [US2] Add a small "Export Applications" button + status poll + download link to `frontend/src/views/CompanyHome.vue`
- [X] T024 [US2] Manually verify via quickstart.md Scenario 2 (immediate response, polling, correct scoping, completion alert, cross-user 404)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Admin/Company get a periodic placement report without asking anyone to compile it (Priority: P2)

**Goal**: A Celery Beat job generates one HTML placement/application report per Company per reporting period, skipping Companies with nothing to report.

**Independent Test**: Trigger the report task, confirm a report appears per Company with activity (and none for a Company with no activity), confirm re-running doesn't duplicate it for the same period.

### Implementation for User Story 3

- [X] T025 [US3] In `app/tasks.py`, add `generate_placement_reports()` (`@celery.task`): for each approved `Company` with at least one `Application` across its drives, compute the period since that Company's last `placement_report` `ExportJob` (or since its `created_at` if none exists), skip if nothing new to report, otherwise render an HTML string (application counts by status, placements in period) and create an `ExportJob(job_type=placement_report, user_id=company.user_id, status=ready, file_path=..., period_start=..., period_end=...)` directly (no polling needed since this job isn't user-triggered), calling `send_email(company.user.email, "report_ready", {...})`
- [X] T026 [US3] Register `generate_placement_reports` in `app/celery_app.py`'s `beat_schedule` (e.g. daily)
- [X] T027 [US3] In `app/routes/company.py`, add `GET /company/reports` and `GET /company/reports/<id>`, per contracts/company-api.md
- [X] T028 [US3] Add a "Placement Reports" list section to `frontend/src/views/CompanyHome.vue` showing period + download link per report
- [X] T029 [US3] Manually verify via quickstart.md Scenario 3 (report generated for active Company, none for inactive Company, no duplicate on re-run)

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T030 Run `make format` (ruff + black) across all touched backend files
- [X] T031 Update `VIVA_PREP.md` (Database Schema, API Reference, Tech Stack, Milestone Map, and a new subsection on background jobs) — stays untracked/gitignored, not part of the PR
- [X] T032 Verify graceful degradation via quickstart.md's final section (`make redis-down`, confirm export requests 503 immediately while everything else keeps working)
- [X] T033 Full manual regression: re-run quickstart.md Scenarios 1-3 end-to-end in one sitting after all tasks above are complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories (Celery/Redis/schema must exist before any task can run)
- **User Stories (Phase 3-5)**: All depend on Foundational. US1 and US2 (both P1) have no dependency on each other. US3 (P2) reuses `ExportJob`/`send_email` from US1/US2's work but only structurally (same table, same helper) — it can be implemented independently once Foundational is done, though doing it last is natural since it's lowest priority.
- **Polish (Phase 6)**: Depends on all three user stories being complete

### Parallel Opportunities

- T004, T005 (Foundational) are marked [P] — different files.
- T008, T011 (Foundational) are marked [P] — different files, no dependency on each other.
- T021, T022, T023 (US2) are marked [P] — different files (company routes, two Vue views).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. Complete Phase 3 (User Story 1) — proves the entire Celery+Redis+email pipeline works
3. **STOP and VALIDATE**: Run quickstart.md Scenario 1
4. Continue with US2 → US3 in priority order, validating each with its quickstart scenario before moving on
