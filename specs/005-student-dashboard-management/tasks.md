# Tasks: Student Dashboard & Job Application System

**Input**: Design documents from `specs/005-student-dashboard-management/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/student-api.md,
quickstart.md

**Tests**: Not included — same decision as Milestones 1-4 (research.md): verify manually via
`quickstart.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6, from spec.md)
- Everything lands in one `StudentHome.vue` view (mirroring Milestones 3-4's single-page pattern),
  so frontend tasks are "add this to StudentHome.vue," not "create a new view/route."
- FR-011 (Company's Applicants filter/sort) isn't its own user story — it's a small extension
  folded into US4's phase, since it exists to support the same "track status" loop from the other
  side.

## Phase 1: Setup

**Purpose**: The schema change every story needs (`Company.overview`, `Application.interview_mode`/
`company_remark`) and clearing the Milestone 2 placeholder.

- [ ] T001 Change `app/models.py`: `Company` gains `overview` (nullable Text); `Application` gains
  `interview_mode` (nullable String) and `company_remark` (nullable Text). Per data-model.md.
- [ ] T002 Autogenerate the migration (`flask db migrate`), review it matches data-model.md exactly,
  apply it (`flask db upgrade`) — depends on T001.
- [ ] T003 [P] Add a sample `Company.overview` value to `data-seeds/seed_data.py`'s seeded Company —
  depends on T001.
- [ ] T004 [P] Remove the Milestone 2 `GET /api/student/ping` placeholder route from
  `app/routes/student.py` (keep the `student_bp` blueprint and its registration).

**Checkpoint**: Migration applied cleanly on a fresh `make db-migrate && make db-seed`;
`student_bp` has no routes yet.

---

## Phase 2: User Story 1 - Student updates their own profile (Priority: P1) 🎯 MVP

**Goal**: A Student can edit every profile field, including a real photo/resume upload, and it's
visible wherever Admin/Company already show that Student's profile.

**Independent Test**: Edit each field, reload, confirm persisted; confirm Admin's Registered
Students view (Milestone 3) shows the same data.

### Implementation for User Story 1

- [ ] T005 [US1] Implement `GET /api/student/profile` in `app/routes/student.py`: returns the
  caller's own `Student` fields plus `photo_url`/`resume_url` via `app/utils.py`'s `static_url()` —
  depends on T004.
- [ ] T006 [US1] Implement `POST /api/student/profile` in `app/routes/student.py`: accepts
  `multipart/form-data`, updates whichever text fields (`name`, `branch`, `graduation_year`, `cgpa`,
  `skills`, `contact`) are provided; saves any `photo`/`resume` file via `werkzeug.secure_filename`
  under `app/static/uploads/{photos,resumes}/`, named `<user_id>_<secure_filename>`, updating
  `photo_path`/`resume_path` — depends on T004.
- [ ] T007 [US1] Create `frontend/src/views/StudentHome.vue` (replacing the Milestone 2 ping
  placeholder): dashboard shell with "edit profile" opening a `Modal.vue` form (text fields + file
  inputs) calling T005/T006 — depends on T005, T006.
- [ ] T008 [US1] Verify per `quickstart.md` → "US1" section: every field persists; the uploaded
  photo/resume shows up in Admin's existing Registered Students view — depends on T006.

**Checkpoint**: User Story 1 fully functional and independently demoable (SC-001).

---

## Phase 3: User Story 2 - Browse Organizations → Company → Drive (Priority: P1)

**Goal**: Student can list approved Companies, open one to see its overview and ongoing Drives, and
open a Drive to see its full detail.

**Independent Test**: Open an approved Company, confirm overview + only its ongoing Drives; open a
Drive, confirm full detail.

### Implementation for User Story 2

- [ ] T009 [US2] Implement `GET /api/student/organizations` in `app/routes/student.py`: `Company`
  query filtered to `approval_status == "approved"`, optional `q` on `company_name` — depends on
  T004.
- [ ] T010 [US2] Implement `GET /api/student/organizations/<id>` in `app/routes/student.py`: `404`
  if not found or not approved, else `overview`/`logo_url`/`industry`/`location` — depends on T004.
- [ ] T011 [US2] Implement `GET /api/student/drives` in `app/routes/student.py`: always filtered to
  `status == "ongoing"` (research.md — not a caller-supplied filter), optional `company_id` and `q`
  (substring on `company_name`/`title`/`drive_name`/`skills_required`) — depends on T004.
- [ ] T012 [US2] Implement `GET /api/student/drives/<id>` in `app/routes/student.py`: no status
  restriction (research.md), full detail including `eligibility_criteria`, `company_logo_url`, and
  `already_applied` (whether the caller has an existing Application to it) — depends on T004.
- [ ] T013 [US2] In `StudentHome.vue`, add "Organizations" (from T009) with a "view details" per row
  opening a Company modal (T010) showing overview + Current Drives (T011 with `company_id`), each
  Drive with its own "view details" opening the Drive modal (T012) — depends on T009, T010, T011,
  T012, T007.
- [ ] T014 [US2] Verify per `quickstart.md` → "US2" section: only approved Companies appear; only a
  Company's own ongoing Drives appear; Drive detail matches what Admin/Company already see for it —
  depends on T009, T010, T011, T012.

**Checkpoint**: User Stories 1-2 both work independently (SC-002).

---

## Phase 4: User Story 3 - Apply to a Drive (Priority: P1)

**Goal**: Student can apply to an ongoing Drive once; a second attempt or an attempt on a completed
Drive is refused.

**Independent Test**: Apply once (succeeds), apply again (refused), apply to a completed Drive
(refused).

### Implementation for User Story 3

- [ ] T015 [US3] Implement `POST /api/student/drives/<id>/apply` in `app/routes/student.py`: `404`
  if no such Drive; `409` if `status == "completed"` or the Student already has an Application to it
  (catching the Milestone 1 `UniqueConstraint`); else creates an `Application` with
  `status="applied"` — depends on T004.
- [ ] T016 [US3] In the Drive modal (T012/T013), show an "Apply" button when `!already_applied`,
  calling T015 and reloading the modal's data on success — depends on T015, T013.
- [ ] T017 [US3] Verify per `quickstart.md` → "US3" section: first Apply succeeds (`201`); second
  Apply on the same Drive refused (`409`); Apply on a `completed` Drive refused (`409`) — depends on
  T015.

**Checkpoint**: User Stories 1-3 all work independently (SC-003).

---

## Phase 5: User Story 4 - Track status, interview, and feedback (Priority: P1)

**Goal**: Student sees every one of their own Applications with status, interview date/time+mode,
and remark; Company can filter/sort its Applicants list to shortlist faster (FR-011).

**Independent Test**: With Applications in a mix of statuses/interview info, load History and
confirm every row is correct; as Company, filter/sort the Applicants list.

### Implementation for User Story 4

- [ ] T018 [US4] Implement `GET /api/student/applications` in `app/routes/student.py`: every
  Application belonging to the caller's own `Student`, including `interview_datetime`,
  `interview_mode`, `company_remark`, and `job_position_id` (for linking back to Drive detail) —
  depends on T004.
- [ ] T019 [US4] Extend `POST /api/company/applications/<id>/decision` in `app/routes/company.py`:
  accept an optional `remark` in the request body, writing `Application.company_remark` alongside
  the existing `status` write — depends on nothing new (existing endpoint from Milestone 4).
- [ ] T020 [US4] Extend `POST /api/company/applications/<id>/interview` in `app/routes/company.py`:
  accept an optional `mode` in the request body, writing `Application.interview_mode` alongside the
  existing `interview_datetime` write — depends on nothing new.
- [ ] T021 [US4] Extend `GET /api/company/drives/<id>/applications` in `app/routes/company.py`:
  optional `status` filter and `sort=status` query params (FR-011) — depends on nothing new.
- [ ] T022 [US4] In `CompanyHome.vue`'s Application-detail modal, add a `remark` text input (calling
  T019) and a `mode` select (calling T020) alongside the existing status dropdown and interview
  date/time field — depends on T019, T020.
- [ ] T023 [US4] In `CompanyHome.vue`'s Applications-list modal, add a status filter dropdown and a
  "sort by status" toggle, re-fetching T021 — depends on T021.
- [ ] T024 [US4] In `StudentHome.vue`, add "Applied Drives" (dashboard summary, from T018) and a
  full "Student Application History" view/modal (Drive No./Interview/Job Title/Results/Remark, from
  the same T018 data) — depends on T018, T007.
- [ ] T025 [US4] Verify per `quickstart.md` → "US4" section and "FR-011" section: Company sets a
  remark+mode, Student sees them exactly as set; Company's Applicants list filters/sorts correctly —
  depends on T018, T019, T020, T021.

**Checkpoint**: User Stories 1-4 all work independently (SC-004).

---

## Phase 6: User Story 5 - Search (Priority: P2)

**Goal**: Student searches ongoing Drives by Company name, Job Title/Drive Name, or skills.

**Independent Test**: A search term matching one Drive returns only it; an unmatched term returns
empty, not an error.

### Implementation for User Story 5

- [ ] T026 [US5] Add a search input to `StudentHome.vue`'s Organizations/Drives area, calling T011
  (already implemented in US2) with `q` set — no new backend endpoint, this is the same
  `GET /api/student/drives` — depends on T011, T013.
- [ ] T027 [US5] Verify per `quickstart.md` → "US5" section: search by Company/title/skills returns
  exact matches; an unmatched term returns `[]`, not an error — depends on T011.

**Checkpoint**: User Stories 1-5 all work independently (SC-005).

---

## Phase 7: User Story 6 - Download placement confirmation (Priority: P3)

**Goal**: Student with a `Placement` record can download a confirmation; a Student without one is
offered nothing.

**Independent Test**: Seed a `Placement`, download and confirm content; a Student with none gets
`404`, not offered a download button.

### Implementation for User Story 6

- [ ] T028 [US6] Implement `GET /api/student/placement/confirmation` in `app/routes/student.py`:
  `404` if no `Placement` row exists for the caller's `Student`, else a `text/plain` response with
  `Content-Disposition: attachment` containing position/company/salary/joining-date — depends on
  T004.
- [ ] T029 [US6] In `StudentHome.vue`, show a "Download Placement Confirmation" button (calling
  T028) only if `GET /api/student/applications` or a dedicated check shows a Placement exists —
  depends on T028, T007.
- [ ] T030 [US6] Verify per `quickstart.md` → "US6" section: download succeeds with correct content
  for a placed Student; `404` for one with none — depends on T028.

**Checkpoint**: All six user stories hold independently (SC-006).

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T031 Verify per `quickstart.md` → "Role check" section: a Company session gets `403` on every
  `/api/student/*` endpoint; no session gets `401` — depends on T005, T009, T010, T011, T012, T015,
  T018, T028.
- [ ] T032 Re-run the full `quickstart.md` end-to-end (backend `curl` pass, then the frontend smoke
  test) against a freshly reseeded database and confirm every SC-00x in spec.md still holds.
- [ ] T033 Commit with the milestone-specific message required by the constitution and push.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **US1-US6 (Phases 2-7)**: each depends only on Setup for their backend endpoints, but
  `StudentHome.vue` is built up incrementally — US2's Organizations/Drives browsing needs US1's
  dashboard shell to exist first, US3 extends US2's Drive modal, US5 extends US2's search-free
  listing, US6 adds one more dashboard element. Build in the order listed: US1 → US2 → US3 → US4 →
  US5 → US6.
- **Polish (Phase 8)**: depends on all six stories.

### Parallel Opportunities

- T001, T003, T004 (Setup, except the migration itself) can run in parallel — different files; T002
  (the migration) depends on T001.
- T005/T006/T009/T010/T011/T012/T015/T018/T028 all land in `app/routes/student.py`; sequence them to
  avoid merge conflicts even though they're logically independent.
- T019/T020/T021 all land in the already-existing `app/routes/company.py`; independent of each
  other and of every `student.py` task, but sequence among themselves to avoid conflicts.
- Every `StudentHome.vue` task (T007, T013, T016, T024, T026, T029) touches the same file — treat as
  sequential for a single implementer, in story order.

---

## Implementation Strategy

### MVP First

1. Setup → US1 (profile).
2. **Stop and validate**: `quickstart.md` US1 section passes end-to-end.

### Incremental Delivery

US2 (browse) → US3 (apply) → US4 (track status/feedback + Company-side filter/sort) → US5 (search)
→ US6 (placement confirmation) → Polish, validating at each checkpoint, then commit (T033).
