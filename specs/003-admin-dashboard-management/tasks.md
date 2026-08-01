# Tasks: Admin Dashboard & Management

**Input**: Design documents from `specs/003-admin-dashboard-management/`

**Prerequisites**: plan.md, spec.md, research.md, contracts/admin-api.md, quickstart.md

**Tests**: Not included — same decision as Milestones 1-2 (research.md): verify manually via
`quickstart.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6, from spec.md)
- Nothing here is truly shared-and-blocking the way Milestone 2's login/logout/me were — every
  endpoint below is independent of the others, sharing only the existing `role_required("admin")`
  decorator and `admin_bp` blueprint from Milestone 2. Setup only clears the placeholder those reused.

## Phase 1: Setup

**Purpose**: Remove the Milestone 2 placeholder this milestone replaces; give the frontend a real
`/admin` route tree for the sub-views each story adds.

- [ ] T001 [P] Remove the Milestone 2 `GET /api/admin/ping` placeholder route from
  `app/routes/admin.py` (keep the `admin_bp` blueprint and its registration in `app/__init__.py` —
  only the placeholder route goes).
- [ ] T002 [P] Add child routes in `frontend/src/router/index.js` for `/admin/companies`,
  `/admin/students`, `/admin/job-postings`, `/admin/applications`, each with `meta.role = "admin"`
  matching the existing `/admin` guard pattern.

**Checkpoint**: `admin_bp` has no routes yet; the frontend has routes with no matching views yet
(expected — each story below adds one).

---

## Phase 2: User Story 1 - Admin sees platform totals (Priority: P1) 🎯 MVP

**Goal**: Admin's dashboard shows live counts of Students, Companies, Job Postings, Applications.

**Independent Test**: `GET /api/admin/dashboard` returns counts matching a direct table count.

### Implementation for User Story 1

- [ ] T003 [US1] Implement `GET /api/admin/dashboard` in `app/routes/admin.py`:
  `User.query.filter_by(role="student").count()`, `Company.query.count()`,
  `JobPosition.query.count()`, `Application.query.count()` — depends on T001.
- [ ] T004 [US1] Replace `frontend/src/views/AdminHome.vue`'s Milestone 2 ping placeholder with a real
  dashboard: fetch T003's endpoint on mount, show the four totals, add nav links to the four sub-views
  added by T002 — depends on T003, T002.
- [ ] T005 [US1] Verify per `quickstart.md` → "US1" section: dashboard counts match a fresh
  registration's effect — depends on T003.

**Checkpoint**: User Story 1 fully functional and independently demoable (SC-001).

---

## Phase 3: User Story 2 - Admin approves/rejects Companies (Priority: P1)

**Goal**: Admin can list, filter, and decide on every Company's approval state; the decision takes
effect immediately for that Company's session.

**Independent Test**: Register a pending Company, approve it via the API, confirm its own
`/api/auth/me` now shows `approved`.

### Implementation for User Story 2

- [ ] T006 [US2] Implement `GET /api/admin/companies` in `app/routes/admin.py`: optional `status` and
  `q` (substring on `company_name`/`industry` via `or_(...ilike(...))`, per research.md) query params
  — depends on T001.
- [ ] T007 [US2] Implement `POST /api/admin/companies/<id>/decision` in `app/routes/admin.py`:
  validates `status` is `approved`/`rejected`, `404` if no such Company, else writes
  `approval_status` and returns it — depends on T001.
- [ ] T008 [US2] Create `frontend/src/views/AdminCompanies.vue`: table of companies from T006, an
  approve/reject action per row calling T007, wired at `/admin/companies` — depends on T006, T007,
  T002.
- [ ] T009 [US2] Verify per `quickstart.md` → "US2" section: pending → approved unlocks the company's
  own state; a second Company rejected stays blocked; a decision can be changed again later (FR-005)
  — depends on T007.

**Checkpoint**: User Stories 1-2 both work independently (SC-002).

---

## Phase 4: User Story 3 - Admin approves/rejects Job Postings (Priority: P2)

**Goal**: Admin can list, filter, and decide on every Job Posting's approval state.

**Independent Test**: With a pending Job Posting from an approved Company, approve it via the API and
confirm its status changes.

### Implementation for User Story 3

- [ ] T010 [US3] Implement `GET /api/admin/job-positions` in `app/routes/admin.py`: optional `status`
  and `q` (substring on `title`/owning Company's `company_name`, joined) query params — depends on
  T001.
- [ ] T011 [US3] Implement `POST /api/admin/job-positions/<id>/decision` in `app/routes/admin.py`:
  same validation/shape as T007, on `JobPosition.status` — depends on T001.
- [ ] T012 [US3] Create `frontend/src/views/AdminJobPostings.vue`: table from T010, approve/reject
  action per row calling T011, wired at `/admin/job-postings` — depends on T010, T011, T002.
- [ ] T013 [US3] Verify per `quickstart.md` → "US3" section: seed a Job Posting via `flask shell`
  (no company-facing "create posting" endpoint exists until Milestone 4), approve it, confirm its
  status — depends on T011.

**Checkpoint**: User Stories 1-3 all work independently.

---

## Phase 5: User Story 4 - Admin searches Companies and Students (Priority: P2)

**Goal**: The `q` param on Company/Student listing narrows results to substring matches; Student
listing/search exists for the first time this milestone.

**Independent Test**: With several seeded accounts, a `q` matching one returns only that one; a `q`
matching none returns `[]`, not an error.

### Implementation for User Story 4

- [ ] T014 [US4] Implement `GET /api/admin/students` in `app/routes/admin.py`: optional `q` (substring
  on `Student.name`, the linked `User.username`, and `Student.contact`, via `or_(...ilike(...))`) —
  depends on T001.
- [ ] T015 [US4] Create `frontend/src/views/AdminStudents.vue`: table from T014 with a search input,
  wired at `/admin/students` — depends on T014, T002.
- [ ] T016 [US4] Add a search input to `AdminCompanies.vue` (T008) that re-fetches T006 with `q` set —
  depends on T008.
- [ ] T017 [US4] Verify per `quickstart.md` → "US4" section: Company search by name/industry
  substring, Student search by name/username/contact substring, and an empty-result case for both —
  depends on T014, T006.

**Checkpoint**: User Stories 1-4 all work independently (SC-003).

---

## Phase 6: User Story 5 - Admin views every Job Posting and Application, any status (Priority: P2)

**Goal**: The same listing endpoints from US3, called with no `status` filter, show every record; a
new endpoint exposes every Application across every Student and Company.

**Independent Test**: With Job Postings in a mix of statuses, calling the listing endpoint with no
filter returns all of them, correctly tagged.

### Implementation for User Story 5

- [ ] T018 [US5] Implement `GET /api/admin/applications` in `app/routes/admin.py`: joins
  `Application` → `Student`/`JobPosition`/`Company` to shape the response per
  `contracts/admin-api.md` — depends on T001.
- [ ] T019 [US5] Create `frontend/src/views/AdminApplications.vue`: table from T018, wired at
  `/admin/applications` — depends on T018, T002.
- [ ] T020 [US5] Confirm `AdminJobPostings.vue` (T012) has a "show all" toggle/default that calls T010
  with no `status` param, not just the pending queue — depends on T012.
- [ ] T021 [US5] Verify per `quickstart.md` → "US5" section: postings across all three statuses all
  appear when unfiltered; applications from multiple students/companies all appear — depends on T010,
  T018.

**Checkpoint**: User Stories 1-5 all work independently (SC-004).

---

## Phase 7: User Story 6 - Admin blacklists/deactivates accounts (Priority: P3)

**Goal**: Admin can flip a Company's or Student's `is_active`, immediately affecting their ability to
log in (Milestone 2's existing check); the Admin account itself can never be targeted.

**Independent Test**: Deactivate an active account, confirm its login is refused per Milestone 2's
existing deactivated-account check; reactivate it and confirm login works again.

### Implementation for User Story 6

- [ ] T022 [US6] Implement `POST /api/admin/users/<id>/toggle-active` in `app/routes/admin.py`:
  `404` if no such user, `403` if the target's `role == "admin"` (FR-012), else flip `is_active` and
  return the new value — mirrors `../hms-app-main/app/routes/admin.py`'s
  `blacklist_doctor`/`blacklist_patient` toggle, per research.md — depends on T001.
- [ ] T023 [US6] Add a deactivate/reactivate action per row to `AdminCompanies.vue` (T008) and
  `AdminStudents.vue` (T015), calling T022 — depends on T022, T008, T015.
- [ ] T024 [US6] Verify per `quickstart.md` → "US6" section: deactivate → login refused (`403`);
  reactivate → login succeeds; attempting to toggle the Admin account itself → `403` — depends on T022.

**Checkpoint**: All six user stories hold independently (SC-005, SC-006).

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T025 Verify per `quickstart.md` → "Role check" section: a Company session calling any
  `/api/admin/*` endpoint directly gets `403` (reusing Milestone 2's `role_required` decorator, not
  new logic to test here) — depends on T003, T006, T010, T014, T018, T022.
- [ ] T026 Re-run the full `quickstart.md` end-to-end (backend `curl` pass, then the frontend smoke
  test) against a freshly reseeded database and confirm every SC-00x in spec.md still holds.
- [ ] T027 Commit with the milestone-specific message required by the constitution and push.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **US1-US6 (Phases 2-7)**: each depends only on Setup (T001/T002) — not on each other, since every
  endpoint and view touches its own files. Built here in the priority order from spec.md (P1 → P1 →
  P2 → P2 → P2 → P3).
- **Polish (Phase 8)**: depends on all six stories.

### Parallel Opportunities

- T001/T002 (Setup) can run in parallel — different files.
- Across stories, the backend endpoint task and frontend view task in each phase touch different
  files and could be split across two people, but the view depends on its endpoint to be
  meaningfully testable — treat as sequential for a single implementer.
- T006/T010/T014/T018/T022 (the five new `app/routes/admin.py` endpoints beyond T003) all land in the
  same file; sequence them to avoid merge conflicts even though they're logically independent.

---

## Implementation Strategy

### MVP First

1. Setup → US1 (dashboard).
2. **Stop and validate**: `quickstart.md` US1 section passes end-to-end.

### Incremental Delivery

US2 (Company decisions) → US3 (Job Posting decisions) → US4 (search) → US5 (view-all) → US6
(deactivate) → Polish, validating at each checkpoint, then commit (T027).
