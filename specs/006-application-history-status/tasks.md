# Tasks: Job Application History and Status Tracking

**Input**: Design documents from `/specs/006-application-history-status/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not requested for this milestone (project convention: manual verification via quickstart.md, no automated test suite).

**Organization**: Tasks are grouped by user story (US1-US4, per spec.md) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

---

## Phase 1: Setup

- [ ] T001 Confirm on branch `feat/milestone-6-status-tracking` off latest `main` (no new dependencies to install for this milestone)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The status-vocabulary rewrite that every user story's display/logic depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 Author Alembic migration in `migrations/versions/` that runs `UPDATE application SET status='interview' WHERE status='waiting'` and `UPDATE application SET status='offer' WHERE status='selected'` in `upgrade()`, with the reverse mapping in `downgrade()` (per data-model.md)
- [ ] T003 Run `flask db upgrade` and verify via `sqlite3 app.db "SELECT DISTINCT status FROM application;"` that no `waiting`/`selected` rows remain
- [ ] T004 Update `data-seeds/seed_data.py`'s sample `Application` to use `status="placed"` instead of `status="selected"` (it already creates a matching `Placement` row — align it with the new invariant that only `placed` applications have one), then re-run `make db-seed` and confirm the app still starts cleanly
- [ ] T004b Create `app/constants.py` defining three enumeration tuples as the single source of truth, replacing scattered literals: `APPLICATION_STATUSES = ("applied", "shortlisted", "interview", "offer", "rejected", "placed")` + `TERMINAL_APPLICATION_STATUSES = ("placed", "rejected")`; `JOB_POSITION_STATUSES = ("ongoing", "completed")`; `COMPANY_APPROVAL_STATUSES = ("pending", "approved", "rejected")`. Update `app/models.py`'s three corresponding `default=...` column args to reference `X[0]` instead of repeating the literal.
- [ ] T004c [P] Create `frontend/src/constants.js` exporting the same three enumerations as ordered `{value, label}` lists, mirroring `app/constants.py`, for Vue views to import instead of hardcoding status strings/labels
- [ ] T004d [P] In `app/routes/admin.py`, replace the literal `COMPANY_DECISION_STATUSES` tuple with `tuple(s for s in COMPANY_APPROVAL_STATUSES if s != "pending")` imported from `app.constants`, and in `complete_job_position` replace the literal `"completed"` with `JOB_POSITION_STATUSES[1]`
- [ ] T004e [P] In `app/routes/company.py`'s `complete_drive`, replace the literal `"completed"` with `JOB_POSITION_STATUSES[1]` imported from `app.constants`
- [ ] T004f [P] In `frontend/src/views/AdminHome.vue` and `frontend/src/views/CompanyHome.vue`, replace hardcoded `?status=ongoing`/`?status=completed`/`?status=pending`/`?status=approved` query-string literals with values from the imported `JOB_POSITION_STATUSES`/`COMPANY_APPROVAL_STATUSES` in `frontend/src/constants.js`

**Checkpoint**: Foundation ready — `Application.status` values are now `applied/shortlisted/interview/offer/rejected/placed` everywhere in the DB; `Application.status`, `JobPosition.status`, and `Company.approval_status` are each defined exactly once in `app/constants.py`/`frontend/src/constants.js` instead of as scattered literals; seed data matches the new vocabulary.

---

## Phase 3: User Story 1 - Company moves an application through the full status lifecycle (Priority: P1) 🎯 MVP

**Goal**: Company can drive an application from Applied through Placed (or to Rejected at any point), with Placed synchronously creating the durable Placement record.

**Independent Test**: As `acme_corp`, move one applicant from Applied to Placed (supplying position/salary/joining date) and confirm a `Placement` row is created; confirm a further status change attempt is rejected.

### Implementation for User Story 1

- [ ] T005 [US1] In `app/routes/company.py`, replace the literal `APPLICATION_DECISION_STATUSES` tuple with `tuple(s for s in APPLICATION_STATUSES if s != "applied")` imported from `app.constants`, and update the `400` error message to match
- [ ] T006 [US1] In `app/routes/company.py`'s `decide_application`, add a terminal-status guard using `app.constants.TERMINAL_APPLICATION_STATUSES`: if `application.status` is already in that tuple, return `409` before applying any change (per contracts/company-api.md)
- [ ] T007 [US1] In `app/routes/company.py`'s `decide_application`, when the new `status == "placed"`: require `position_title` and `joining_date` in the request body (`400` if missing), parse `joining_date` as an ISO date, and create a `Placement` row (`student_id`/`company_id` from `application.student`/`application.job_position.company`, `application_id=application.id`, `position_title`, `salary`, `joining_date`) in the same transaction, importing `Placement` at the top of the file
- [ ] T008 [P] [US1] In `frontend/src/views/CompanyHome.vue`, replace the hardcoded status `<select>` options in the "Student Application" modal with `v-for` over the imported `APPLICATION_STATUSES` from `frontend/src/constants.js`, and add inline inputs for position title/salary/joining date plus a "Confirm Placement" action that only appears/applies when `placed` is selected, calling `setStatus` with the extra fields
- [ ] T009 [US1] Manually verify via quickstart.md Scenario 1 (full lifecycle Applied→...→Placed, confirm Placement created, confirm further status change is rejected)

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Student views complete application and placement history in one place (Priority: P1)

**Goal**: A Student's history view shows every application's status, interview info, remark, and (once Placed) placement outcome, without opening each drive.

**Independent Test**: As `john_doe`, open the History view and confirm the seeded Placed application shows its placement outcome alongside status/interview/remark.

### Implementation for User Story 2

- [ ] T010 [US2] In `app/routes/student.py`'s `_application_payload`, add a `"placement"` field: `None` unless `application.status == "placed"`, in which case a dict with `position_title`/`salary`/`joining_date` from that application's `Placement` row (query `Placement.query.filter_by(application_id=application.id).first()`)
- [ ] T011 [P] [US2] In `frontend/src/views/StudentHome.vue`'s History modal table, add a "Placement" column/row that shows `a.placement.position_title` (and salary/joining date) when `a.placement` is present, otherwise blank; also switch the existing "Results" column from the raw `a.status` string to its `label` via `frontend/src/constants.js`'s `APPLICATION_STATUSES`
- [ ] T012 [US2] Manually verify via quickstart.md Scenario 2 (History view shows all statuses plus placement outcome for the Placed one)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Admin and Company can view a Student's full profile (Priority: P2)

**Goal**: Admin gets a full Student profile + application-history detail view; Company's existing applicant-review view gains the two profile fields it was missing.

**Independent Test**: As Admin, open a Student's profile from the Students list and see every profile field plus their full application history. As `acme_corp`, open an applicant and see graduation year/contact alongside the existing CGPA/branch/skills.

### Implementation for User Story 3

- [ ] T013 [US3] In `app/routes/admin.py`, add `GET /admin/students/<int:student_id>` (`role_required("admin")`, `404` if not found) returning the Student's full profile (reuse the shape of `student.py`'s `_profile_payload`: name, branch, graduation_year, cgpa, skills, contact, photo_url, resume_url) plus an `"applications"` list (job_title, company_name, status, application_date, interview_datetime, interview_mode, company_remark, placement — same placement rule as T010), per contracts/admin-api.md
- [ ] T014 [P] [US3] In `app/routes/company.py`'s `_application_detail_payload`, add `"student_graduation_year": student.graduation_year` and `"student_contact": student.contact`, per contracts/company-api.md
- [ ] T015 [P] [US3] In `frontend/src/views/AdminHome.vue`, add a "View Profile" button per row in the "Registered Students" section that fetches `GET /admin/students/<id>` and opens a new modal showing the full profile fields and an application-history table (status shown via `frontend/src/constants.js`'s `APPLICATION_STATUSES` label lookup, same as T011)
- [ ] T016 [P] [US3] In `frontend/src/views/CompanyHome.vue`'s "Student Application" modal, add `<p><strong>Graduation Year:</strong> {{ selectedApplication.student_graduation_year }}</p>` and `<p><strong>Contact:</strong> {{ selectedApplication.student_contact }}</p>`
- [ ] T017 [US3] Manually verify via quickstart.md Scenario 3 (Admin profile+history modal; Company sees graduation year/contact)

**Checkpoint**: User Stories 1, 2, and 3 all work independently.

---

## Phase 6: User Story 4 - Students only ever see and apply to drives from currently-approved companies (Priority: P2)

**Goal**: Revoking a Company's approval immediately hides its drives from Student-facing views and blocks new applications, without touching existing history.

**Independent Test**: Revoke an approved Company's approval after it has an ongoing drive; confirm the drive disappears from Student listings and a direct apply attempt 404s, while that Company's existing applicants' history stays visible everywhere else.

### Implementation for User Story 4

- [ ] T018 [US4] In `app/routes/student.py`'s `list_drives`, add `.filter(Company.approval_status == "approved")` to the existing join (per contracts/student-api.md)
- [ ] T019 [US4] In `app/routes/student.py`'s `get_drive`, after loading the drive, return `404` if `drive.company.approval_status != "approved"` (same 404 message/shape as "Drive not found")
- [ ] T020 [US4] In `app/routes/student.py`'s `apply_to_drive`, after loading the drive, return `404` if `drive.company.approval_status != "approved"` (before the existing completed/duplicate checks)
- [ ] T021 [US4] Manually verify via quickstart.md Scenario 4 (revoke approval, confirm drive disappears/blocks apply, confirm prior history for that company stays visible in Student/Admin/Company views)

**Checkpoint**: All four user stories are independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T022 Run `make format` (ruff + black) across all touched backend files
- [ ] T023 Update `VIVA_PREP.md`'s API Reference, Database Schema, and Milestone Map sections to reflect the new status vocabulary, the new `/admin/students/<id>` endpoint, and Milestone 6 moving to ✅ (per the user's "keep it a running document" instruction — this file stays untracked/gitignored, not part of the PR)
- [ ] T024 Full manual regression: re-run quickstart.md Scenarios 1-4 end-to-end in one sitting after all tasks above are complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories (status vocabulary must be correct in the DB before any story's logic or display is meaningful)
- **User Stories (Phase 3-6)**: All depend on Foundational. US1 and US2 (both P1) have no dependency on each other or on US3/US4. US3 and US4 (both P2) have no dependency on each other, though US3's admin history display and US4's approval gating are easiest to verify once US1/US2 exist (their Placed/placement data gives US3's history view something to show).
- **Polish (Phase 7)**: Depends on all four user stories being complete

### Parallel Opportunities

- T008 (Vue) can proceed alongside T005-T007 (backend) once the API contract (contracts/company-api.md) is fixed — implement backend first in practice since the same person is doing both, but they don't block each other structurally.
- T011, T014, T015, T016 are all marked [P] — different files, no cross-dependencies.
- US3 (Phase 5) and US4 (Phase 6) can be implemented in either order or interleaved.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. Complete Phase 3 (User Story 1) — this alone fixes the "Placement never gets created" bug and delivers the core status lifecycle
3. **STOP and VALIDATE**: Run quickstart.md Scenario 1
4. Continue with US2 → US3 → US4 in priority order, validating each with its quickstart scenario before moving on
