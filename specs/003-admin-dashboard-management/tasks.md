# Tasks: Admin Dashboard & Management

**Input**: Design documents from `specs/003-admin-dashboard-management/`

**Prerequisites**: plan.md, spec.md, research.md, contracts/admin-api.md, quickstart.md

**Tests**: Not included — same decision as Milestones 1-2 (research.md): verify manually via
`quickstart.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5, from spec.md)
- Everything lands in one `AdminHome.vue` view now (single-page redesign), so frontend tasks are
  "add this subsection to AdminHome.vue," not "create a new view/route."

## Phase 1: Setup

**Purpose**: Clear the Milestone 2 placeholder; change `JobPosition.status`'s default and seed value
to match the new ongoing/completed lifecycle; add the shared `Modal.vue`.

- [ ] T001 [P] Remove the Milestone 2 `GET /api/admin/ping` placeholder route from
  `app/routes/admin.py` (keep the `admin_bp` blueprint and its registration).
- [ ] T002 [P] Change `JobPosition.status`'s default in `app/models.py` from `"pending"` to
  `"ongoing"`; update `data-seeds/seed_data.py`'s sample Job Posting to `status="ongoing"` (was
  `"approved"`) — no migration needed, same column/type.
- [ ] T003 [P] Create `frontend/src/components/Modal.vue`: a prop-driven (`show`, `title`) component
  styled with Bootstrap's `.modal`/`.modal-dialog`/`.modal-content` classes, toggled with `v-if` — no
  Bootstrap JS bundle (per research.md).
- [ ] T004 Remove the `/admin/companies`, `/admin/students`, `/admin/job-postings`,
  `/admin/applications` child routes from `frontend/src/router/index.js` if present from an earlier
  draft — `/admin` is the only Admin route now.

**Checkpoint**: `admin_bp` has no routes yet; `Modal.vue` exists but nothing uses it yet.

---

## Phase 2: User Story 1 - Company approve/reject (Priority: P1) 🎯 MVP

**Goal**: Admin can list pending Companies and decide on each; approving is what unlocks Drive
creation for that Company.

**Independent Test**: Register a pending Company, approve it, confirm it now appears under
`status=approved` and no longer under `status=pending`.

### Implementation for User Story 1

- [ ] T005 [US1] Implement `GET /api/admin/companies` in `app/routes/admin.py`: optional `status` and
  `q` query params (substring on `company_name`/`industry` via `or_(...ilike(...))`) — depends on T001.
- [ ] T006 [US1] Implement `POST /api/admin/companies/<id>/decision` in `app/routes/admin.py`:
  validates `status` is `approved`/`rejected`, `404` if no such Company, else writes
  `approval_status` and returns it — depends on T001.
- [ ] T007 [US1] In `AdminHome.vue`, add the "Company Applications" subsection: table of
  `status=pending` Companies from T005, Approve (green) and Reject buttons calling T006, reloading the
  list after each — depends on T005, T006.
- [ ] T008 [US1] Verify per `quickstart.md` → "US1" section: approve moves a Company from pending to
  approved; reject removes it from both — depends on T006.

**Checkpoint**: User Story 1 fully functional and independently demoable (SC-002, SC-003).

---

## Phase 3: User Story 2 - Blacklist/whitelist Companies and Students (Priority: P1)

**Goal**: Admin can list Registered Companies and Students and flip their active state; the Admin
account itself can never be targeted.

**Independent Test**: Blacklist an active account, confirm login is refused; whitelist it, confirm
login works again; attempt to blacklist Admin, confirm refusal.

### Implementation for User Story 2

- [ ] T009 [US2] Implement `GET /api/admin/students` in `app/routes/admin.py`: optional `q` (substring
  on `Student.name`, linked `User.username`, `Student.contact`) — depends on T001.
- [ ] T010 [US2] Implement `POST /api/admin/users/<id>/toggle-active` in `app/routes/admin.py`:
  `404` if no such user, `403` if target's `role == "admin"`, else flip `is_active` and return it —
  mirrors `../hms-app-main/app/routes/admin.py`'s blacklist toggle, per research.md — depends on T001.
- [ ] T011 [US2] In `AdminHome.vue`, add the "Registered Companies" subsection: table of
  `status=approved` Companies from T005, a Blacklist/Whitelist button per row (label + color driven by
  `is_active`) calling T010 — depends on T005, T010.
- [ ] T012 [US2] In `AdminHome.vue`, add the "Registered Students" subsection: table of Students from
  T009, same Blacklist/Whitelist button pattern as T011 — depends on T009, T010.
- [ ] T013 [US2] Verify per `quickstart.md` → "US2" section: blacklist → login `403`; whitelist →
  login `200`; toggling the Admin account itself → `403` — depends on T010.

**Checkpoint**: User Stories 1-2 both work independently (SC-005, SC-006).

---

## Phase 4: User Story 3 - Search Companies and Students together (Priority: P2)

**Goal**: One search field in Section 1 filters Registered Companies and Registered Students
simultaneously.

**Independent Test**: A search term matching one account narrows both lists correctly; an empty term
resets both to unfiltered.

### Implementation for User Story 3

- [ ] T014 [US3] Add the Section 1 header to `AdminHome.vue`: "Welcome Admin" text, the live totals
  from `GET /api/admin/dashboard` (already implemented in the original draft, unchanged endpoint), one
  search input + Search button — depends on T007, T011, T012 (needs the lists it will filter to exist).
- [ ] T015 [US3] Wire the Section 1 search input to re-fetch T005 (`GET /api/admin/companies`,
  keeping `status=approved`) and T009 (`GET /api/admin/students`) with `q` set, updating Registered
  Companies and Registered Students only — depends on T014.
- [ ] T016 [US3] Verify per `quickstart.md` → "US3" section: search narrows both lists correctly; an
  unmatched term empties both without erroring — depends on T015.

**Checkpoint**: User Stories 1-3 all work independently (SC-001, SC-004).

---

## Phase 5: User Story 4 - Ongoing Drives: view details, mark complete (Priority: P2)

**Goal**: Admin can see every non-completed Drive, inspect one's full detail in a modal, and mark it
complete.

**Independent Test**: Seed an ongoing Drive, view its details, mark it complete, confirm it's gone
from the list.

### Implementation for User Story 4

- [ ] T017 [US4] Implement `GET /api/admin/job-positions` in `app/routes/admin.py`: optional `status`
  query param; response includes every field the "View Details" modal needs (description,
  eligible_branches, min_cgpa, eligible_graduation_year, salary, skills_required,
  application_deadline, company_name) so no separate detail endpoint is needed — depends on T001, T002.
- [ ] T018 [US4] Implement `POST /api/admin/job-positions/<id>/complete` in `app/routes/admin.py`:
  `404` if no such Drive, else sets `status="completed"` and returns it — depends on T001.
- [ ] T019 [US4] In `AdminHome.vue`, add the "Ongoing Drives" subsection: table (Serial Number, Drive
  Name) from T017 with `status=ongoing`, a "View Details" button opening `Modal.vue` (T003) with the
  full row data, and a "Mark as Complete" button calling T018 and reloading the list — depends on
  T017, T018, T003.
- [ ] T020 [US4] Verify per `quickstart.md` → "US4" section: seed a Drive via `flask shell`, confirm
  its default status is `"ongoing"`; view details shows full info; mark complete removes it from the
  list — depends on T017, T018.

**Checkpoint**: User Stories 1-4 all work independently (SC-007).

---

## Phase 6: User Story 5 - Student Applications, read-only (Priority: P3)

**Goal**: Admin can see every Application and inspect one's detail in a read-only modal.

**Independent Test**: With several Applications, load the list and confirm every one appears; open one
in the modal and confirm no action buttons are present.

### Implementation for User Story 5

- [ ] T021 [US5] Implement `GET /api/admin/applications` in `app/routes/admin.py`: joins
  `Application` → `Student`/`JobPosition`/`Company` per `contracts/admin-api.md` — depends on T001.
- [ ] T022 [US5] In `AdminHome.vue`, add the "Student Applications" subsection: table (Serial Number,
  Student Name, Drive, Company, Date) from T021, a "View" button opening `Modal.vue` (T003) with the
  row's detail and no action buttons — depends on T021, T003.
- [ ] T023 [US5] Verify per `quickstart.md` → "US5" section: every Application appears; compare the
  list's count to a direct table count to confirm 100% coverage (SC-008) — depends on T021.

**Checkpoint**: All five user stories hold independently.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T024 Verify per `quickstart.md` → "Role check" section: a Company session calling any
  `/api/admin/*` endpoint directly gets `403` — depends on T005, T009, T010, T017, T018, T021.
- [ ] T025 Re-run the full `quickstart.md` end-to-end (backend `curl` pass, then the frontend smoke
  test) against a freshly reseeded database and confirm every SC-00x in spec.md still holds.
- [ ] T026 Commit with the milestone-specific message required by the constitution and push.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **US1-US5 (Phases 2-6)**: each depends only on Setup — not on each other for their backend
  endpoints, but the Section 1 search/header task (T014) depends on the Registered
  Companies/Students subsections existing first (T007/T011/T012), so build in the order listed:
  US1 → US2 → US3 → US4 → US5.
- **Polish (Phase 7)**: depends on all five stories.

### Parallel Opportunities

- T001-T004 (Setup) can all run in parallel — different files.
- T005/T009/T010/T017/T018/T021 all land in `app/routes/admin.py`; sequence them to avoid merge
  conflicts even though they're logically independent.
- Every `AdminHome.vue` subsection task (T007, T011, T012, T019, T022) touches the same file — treat
  as sequential for a single implementer, in story order.

---

## Implementation Strategy

### MVP First

1. Setup → US1 (Company approve/reject).
2. **Stop and validate**: `quickstart.md` US1 section passes end-to-end.

### Incremental Delivery

US2 (blacklist/whitelist) → US3 (search) → US4 (Ongoing Drives) → US5 (Student Applications) →
Polish, validating at each checkpoint, then commit (T026).
