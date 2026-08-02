# Tasks: Company Dashboard & Job/Application Management

**Input**: Design documents from `specs/004-company-dashboard-management/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/company-api.md,
quickstart.md

**Tests**: Not included — same decision as Milestones 1-3 (research.md): verify manually via
`quickstart.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5, from spec.md)
- Everything lands in one `CompanyHome.vue` view (mirroring Milestone 3's single-page pattern), so
  frontend tasks are "add this to CompanyHome.vue," not "create a new view/route."

## Phase 1: Setup

**Purpose**: The schema change every story needs (drive_name/eligibility_criteria/
interview_datetime, dropping the three unused eligibility columns) and the approval-gate decorator.

- [ ] T001 Change `app/models.py`: `JobPosition` gains `drive_name` (nullable, required at the API
  layer) and `eligibility_criteria` (nullable Text); drops `eligible_branches`, `min_cgpa`,
  `eligible_graduation_year`. `Application` gains `interview_datetime` (nullable DateTime). Per
  data-model.md.
- [ ] T002 Autogenerate the migration (`flask db migrate`), review it matches data-model.md exactly,
  apply it (`flask db upgrade`) — depends on T001.
- [ ] T003 [P] Update `data-seeds/seed_data.py`'s sample Job Posting: add `drive_name` and
  `eligibility_criteria` values, remove the three dropped fields — depends on T001.
- [ ] T004 [P] Add `company_approved_required` to `app/decorators.py`: wraps `role_required("company")`,
  additionally checks `current_user.company_profile.approval_status == "approved"`, returns
  `{"error": "Company is not yet approved"}`, `403` if not (per research.md).
- [ ] T005 [P] Remove the Milestone 2 `GET /api/company/ping` placeholder route from
  `app/routes/company.py` (keep the `company_bp` blueprint and its registration).

**Checkpoint**: Migration applied cleanly on a fresh `make db-migrate && make db-seed`;
`company_bp` has no routes yet.

---

## Phase 2: User Story 1 - Create a Drive (Priority: P1) 🎯 MVP

**Goal**: An approved Company can create a Drive; a pending/rejected one is refused.

**Independent Test**: Submit the Create Drive form as an approved Company, confirm it appears in
Upcoming Drives; attempt the same as a pending Company, confirm refusal.

### Implementation for User Story 1

- [ ] T006 [US1] Implement `POST /api/company/drives` in `app/routes/company.py`: validates
  `drive_name`, `title`, `application_deadline` present, creates a `JobPosition` owned by
  `current_user.company_profile`, defaulting `status="ongoing"` — decorated with
  `company_approved_required` — depends on T001, T004, T005.
- [ ] T007 [US1] In `CompanyHome.vue`, replace the Milestone 2 ping placeholder with the dashboard
  shell (page header, "Create Drive" button) and a Create Drive modal (reusing `Modal.vue`) with
  fields matching the wireframe: Drive Name, Job Title, Job Description, Eligibility Criteria,
  Application Deadline — depends on T006.
- [ ] T008 [US1] Verify per `quickstart.md` → "US1" section: create succeeds and appears in Upcoming
  Drives; a pending Company's attempt gets `403` "Company is not yet approved" — depends on T006.

**Checkpoint**: User Story 1 fully functional and independently demoable (SC-001).

---

## Phase 3: User Story 2 - Upcoming/Closed Drives, mark complete (Priority: P1)

**Goal**: Company sees only its own Drives split by status, and can close one.

**Independent Test**: With Drives in both states, confirm each list shows only this Company's own
matching rows; mark one complete and confirm it moves lists.

### Implementation for User Story 2

- [ ] T009 [US2] Implement `GET /api/company/drives` in `app/routes/company.py`: optional `status`
  filter, scoped to `current_user.company_profile.job_positions` only — decorated with
  `company_approved_required` — depends on T001, T004, T005.
- [ ] T010 [US2] Implement `POST /api/company/drives/<id>/complete` in `app/routes/company.py`: `404`
  if the Drive doesn't exist or isn't owned by the caller's Company, else sets `status="completed"` —
  depends on T004, T005.
- [ ] T011 [US2] In `CompanyHome.vue`, add Upcoming Drives (Sr No, Drive Name, "view details",
  "mark as complete") and Closed Drives (Sr No, Drive Name, "update") tables from T009 — "mark as
  complete" calls T010 and reloads — depends on T009, T010, T007.
- [ ] T012 [US2] Verify per `quickstart.md` → "US2" section: each list shows only this Company's own
  Drives in the right status; marking complete moves a Drive between lists immediately — depends on
  T009, T010.

**Checkpoint**: User Stories 1-2 both work independently (SC-002, SC-003).

---

## Phase 4: User Story 3 - Review a Drive's Applicants (Priority: P1)

**Goal**: Company sees every Applicant for one of its own Drives; refused for a Drive it doesn't own.

**Independent Test**: Open a Drive's Applications list, confirm every applicant to that specific Drive
appears and no one else's; attempt against another Company's Drive ID, confirm `404`.

### Implementation for User Story 3

- [ ] T013 [US3] Implement `GET /api/company/drives/<id>/applications` in `app/routes/company.py`:
  `404` if the Drive isn't owned by the caller's Company, else every `Application` against it —
  decorated with `company_approved_required` — depends on T004, T005.
- [ ] T014 [US3] In `CompanyHome.vue`, wire both Upcoming Drives' "view details" and Closed Drives'
  "update" to open the same Applications-list modal (reusing `Modal.vue`) from T013, each row with a
  "review application" button — depends on T013, T011.
- [ ] T015 [US3] Verify per `quickstart.md` → "US3" section: every applicant for a Drive appears;
  "update" on a Closed Drive opens the same list; a cross-Company Drive ID gets `404` — depends on
  T013.

**Checkpoint**: User Stories 1-3 all work independently (SC-003).

---

## Phase 5: User Story 4 - Review one Application and set its status (Priority: P1)

**Goal**: Company sees one Application's full detail and can set its status; refused for another
Company's Application.

**Independent Test**: Open an Application, set each of the four statuses in turn, confirm each sticks;
attempt against another Company's Application, confirm `404`.

### Implementation for User Story 4

- [ ] T016 [US4] Implement `GET /api/company/applications/<id>` in `app/routes/company.py`: `404` if
  the Application's Drive isn't owned by the caller's Company, else full detail per
  contracts/company-api.md (student name/branch/photo/resume, drive name, job title, status,
  interview_datetime) — depends on T004, T005.
- [ ] T017 [US4] Implement `POST /api/company/applications/<id>/decision` in `app/routes/company.py`:
  validates `status` is one of `shortlisted`/`waiting`/`selected`/`rejected`, same ownership check as
  T016 — depends on T004, T005.
- [ ] T018 [US4] In `CompanyHome.vue`, "review application" swaps the Applications-list modal (T014)
  for an Application-detail modal from T016: student name/branch, photo, "view resume" link, Drive/
  Job Title, a status dropdown calling T017, and a "Back" button returning to the Applications list —
  depends on T016, T017, T014.
- [ ] T019 [US4] Verify per `quickstart.md` → "US4" section: each of the four statuses is set and
  persists; the photo/resume URLs match what Admin already sees for that Student (Milestone 3); a
  cross-Company Application ID gets `404` — depends on T016, T017.

**Checkpoint**: User Stories 1-4 all work independently (SC-004).

---

## Phase 6: User Story 5 - Schedule an interview (Priority: P2)

**Goal**: Company can set (and change) an interview date/time on any Application, independent of its
status.

**Independent Test**: Set an interview date/time on an Application, confirm it persists; confirm it's
optional (absent by default).

### Implementation for User Story 5

- [ ] T020 [US5] Implement `POST /api/company/applications/<id>/interview` in `app/routes/company.py`:
  validates `interview_datetime` is present and a valid ISO datetime, same ownership check as T016 —
  depends on T004, T005.
- [ ] T021 [US5] In the Application-detail modal (T018), add an interview date/time input calling
  T020, alongside the existing status dropdown — depends on T020, T018.
- [ ] T022 [US5] Verify per `quickstart.md` → "US5" section: setting an interview date/time persists
  across a reload; an Application with none set shows the field empty, not an error — depends on T020.

**Checkpoint**: All five user stories hold independently (SC-005).

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T023 Verify per `quickstart.md` → "Role/approval check" section: a Student session gets `403` on
  every `/api/company/*` endpoint; no session gets `401` — depends on T006, T009, T010, T013, T016,
  T017, T020.
- [ ] T024 Re-run the full `quickstart.md` end-to-end (backend `curl` pass, then the frontend smoke
  test) against a freshly reseeded database and confirm every SC-00x in spec.md still holds.
- [ ] T025 Commit with the milestone-specific message required by the constitution and push.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **US1-US5 (Phases 2-6)**: each depends only on Setup for their backend endpoints, but the frontend
  build order matters — US3's Applications modal needs US2's Drive tables to open it from, and US4/
  US5 both extend the same Application-detail modal — build in the order listed: US1 → US2 → US3 →
  US4 → US5.
- **Polish (Phase 7)**: depends on all five stories.

### Parallel Opportunities

- T001, T003-T005 (Setup, except the migration itself) can run in parallel — different files; T002
  (the migration) depends on T001.
- T006/T009/T010/T013/T016/T017/T020 all land in `app/routes/company.py`; sequence them to avoid
  merge conflicts even though they're logically independent.
- Every `CompanyHome.vue` task (T007, T011, T014, T018, T021) touches the same file — treat as
  sequential for a single implementer, in story order.

---

## Implementation Strategy

### MVP First

1. Setup → US1 (Create a Drive).
2. **Stop and validate**: `quickstart.md` US1 section passes end-to-end.

### Incremental Delivery

US2 (Upcoming/Closed Drives) → US3 (Applicants list) → US4 (review/decide) → US5 (interview
scheduling) → Polish, validating at each checkpoint, then commit (T025).
