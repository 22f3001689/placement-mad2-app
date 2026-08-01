# Tasks: Authentication & Role-Based Access

**Input**: Design documents from `specs/002-auth-role-based-access/`

**Prerequisites**: plan.md, spec.md, research.md, contracts/auth-api.md, quickstart.md

**Tests**: Not included — same decision as Milestone 1 (research.md): verify manually via
`quickstart.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US4, from spec.md)
- `login`/`logout`/`me` are shared by every story, so they live in Foundational, not a specific
  story phase — each story then only adds what's actually specific to it (its register endpoint, its
  placeholder landing page, its role-gated "ping" endpoint).

## Phase 1: Setup

**Purpose**: Frontend project exists; Flask has somewhere to serve it from; the one shared
authorization primitive exists.

- [ ] T001 [P] Scaffold `frontend/`: Vite + Vue 3 + Vue Router (`npm create vite@latest`, Vue
  template, add `vue-router`). `vite.config.js`: dev proxy `/api` → `http://localhost:5000`;
  `build.outDir` → `../app/static/dist`; stable (non-hashed) output filenames (per research.md).
- [ ] T002 [P] Add `app/templates/index.html`: the one Jinja shell — Bootstrap via CDN `<link>`, a
  `<div id="app"></div>` mount point, and `<script type="module" src="{{ url_for('static',
  filename='dist/index.js') }}">` — no other markup.
- [ ] T003 Add a catch-all route (in `app/__init__.py` or a small `app/routes/frontend.py`) that
  renders `index.html` for `/` and any path not starting with `/api` — depends on T002.
- [ ] T004 Create `app/decorators.py` with `role_required(*roles)`, wrapping `flask_login.
  login_required` plus a role check that `abort(403)`s on mismatch.

**Checkpoint**: `flask run` serves the Vite-built shell at `/`; `frontend/` builds.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Login, logout, and "who am I" — every story needs all three; nothing story-specific can
be demoed without them.

- [ ] T005 Create `app/routes/auth.py` (`auth_bp`) and register it in `app/__init__.py` — depends on
  T004.
- [ ] T006 Implement `POST /api/auth/login` in `app/routes/auth.py`: look up by username, check
  password, reject with `401` if either is wrong (same message, FR-006), reject with `403` if
  `is_active` is False (FR-005), else `login_user()` and return role (+ `approval_status` if company)
  — adapted from `../hms-app-main/app/routes/auth.py`'s login view, JSON instead of
  form+redirect — depends on T005.
- [ ] T007 Implement `POST /api/auth/logout` in `app/routes/auth.py`: `login_required` +
  `logout_user()` — depends on T005.
- [ ] T008 Implement `GET /api/auth/me` in `app/routes/auth.py`: `login_required`, returns the same
  shape as login's success response — depends on T005.
- [ ] T009 [P] Create `frontend/src/api/http.js`: a thin `fetch` wrapper that always sends
  `credentials: 'include'` and parses JSON/error bodies.
- [ ] T010 [P] Create `frontend/src/state/auth.js`: one `reactive({ user: null })` plus
  `login()`/`logout()`/`fetchMe()` helpers that call T009's wrapper.
- [ ] T011 Create `frontend/src/router/index.js`: base router with a global navigation guard that
  calls `state.auth.fetchMe()` once and redirects to `/login` for any protected route with no user —
  depends on T010.
- [ ] T012 Create `frontend/src/views/Login.vue` and wire it at `/login` — depends on T009, T010,
  T011.

**Checkpoint**: `curl` login/logout/me all work; `Login.vue` can log in and the auth state updates.

---

## Phase 3: User Story 1 - Student self-registers and logs in (Priority: P1) 🎯 MVP

**Goal**: A Student can create their own account and reach a Student-only landing page.

**Independent Test**: Register a new Student via the API, log in, confirm `/api/student/ping`
succeeds and reflects the student session.

### Implementation for User Story 1

- [ ] T013 [US1] Implement `POST /api/auth/register/student` in `app/routes/auth.py`: unique
  username, password ≥ 6 chars, creates `User(role="student")` + `Student` profile — depends on T005.
- [ ] T014 [US1] Implement `GET /api/student/ping` (new `app/routes/student.py` blueprint, registered
  in `app/__init__.py`), decorated with `role_required("student")`, returning a small greeting JSON —
  depends on T004, T005.
- [ ] T015 [US1] Create `frontend/src/views/RegisterStudent.vue` + router entry `/register/student`
  — depends on T012.
- [ ] T016 [US1] Create `frontend/src/views/StudentHome.vue` (calls `/api/student/ping`, shows the
  greeting) + router entry `/student` — depends on T014, T011.
- [ ] T017 [US1] Verify per `quickstart.md` → "US1" section: register, login, `me`, duplicate
  username → `409` — depends on T013.

**Checkpoint**: User Story 1 fully functional and independently demoable (SC-001).

---

## Phase 4: User Story 2 - Admin has exactly one, predefined login (Priority: P1)

**Goal**: The seeded Admin account logs in and reaches an Admin-only landing page; no registration
path for Admin exists anywhere.

**Independent Test**: Confirm no `register/admin` route exists at all, then log in with the seeded
Admin credentials and reach `/api/admin/ping`.

### Implementation for User Story 2

- [ ] T018 [US2] Implement `GET /api/admin/ping` (new `app/routes/admin.py` blueprint, registered in
  `app/__init__.py`), decorated with `role_required("admin")` — depends on T004, T005.
- [ ] T019 [US2] Create `frontend/src/views/AdminHome.vue` (calls `/api/admin/ping`) + router entry
  `/admin` — depends on T018, T011.
- [ ] T020 [US2] Verify per `quickstart.md` → "US2" section: `register/admin` → `404`; admin login
  → `200` with role `admin` — depends on T006.

**Checkpoint**: User Stories 1-2 both work independently (SC-004).

---

## Phase 5: User Story 3 - Company registers, logs in, sees its real approval state (Priority: P1)

**Goal**: A Company can create its own account, log in immediately, and see whether it's pending or
approved — with company-only capability gated on that state.

**Independent Test**: Register a new Company, log in while still pending, confirm `/api/company/ping`
reflects `approval_status: "pending"`.

### Implementation for User Story 3

- [ ] T021 [US3] Implement `POST /api/auth/register/company` in `app/routes/auth.py`: unique
  username, password ≥ 6 chars, creates `User(role="company")` + `Company` profile with
  `approval_status="pending"` — depends on T005.
- [ ] T022 [US3] Implement `GET /api/company/ping` (in `app/routes/company.py`, new blueprint),
  decorated with `role_required("company")`; always returns `200` with the real
  `approval_status` — pending Companies still get a response, only company-only *capabilities* (none
  exist until Milestone 4) are meant to be gated on it (FR-008/FR-009) — depends on T004, T005.
- [ ] T023 [US3] Create `frontend/src/views/RegisterCompany.vue` + router entry
  `/register/company` — depends on T012.
- [ ] T024 [US3] Create `frontend/src/views/CompanyHome.vue` (calls `/api/company/ping`, shows the
  pending/approved state plainly) + router entry `/company` — depends on T022, T011.
- [ ] T025 [US3] Verify per `quickstart.md` → "US3" section: register, login, pending state visible
  via `/api/auth/me` and `/api/company/ping` — depends on T021.

**Checkpoint**: User Stories 1-3 all work independently (SC-002).

---

## Phase 6: User Story 4 - No cross-role access, ever (Priority: P2)

**Goal**: Every role boundary from US1-3 actually holds under direct attack, not just in the UI.

**Independent Test**: Logged in as Student, call `/api/company/ping` and `/api/admin/ping` directly;
both must refuse.

### Implementation for User Story 4

- [ ] T026 [US4] Add a per-route `meta.role` check to the navigation guard in
  `frontend/src/router/index.js`: redirect to the user's own home if they're logged in as the wrong
  role for the target route — depends on T016, T019, T024.
- [ ] T027 [US4] Verify per `quickstart.md` → "US4" section: as Student, `curl` both
  `/api/company/ping` and `/api/admin/ping` directly → `403` both; as Company, `curl`
  `/api/admin/ping` → `403` — depends on T014, T018, T022.
- [ ] T028 [US4] Verify: log out, then `GET /api/auth/me` → `401`; in the browser, visiting a
  protected route while logged out redirects to `/login` — depends on T007, T026.
- [ ] T029 [US4] Verify the deactivated-account edge case per `quickstart.md`: flip `is_active` to
  `False` via `flask shell`, confirm login now returns `403` despite the correct password —
  depends on T006.

**Checkpoint**: All four user stories hold independently, including under direct/adversarial
requests (SC-003, SC-005).

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T030 Re-run the full `quickstart.md` end-to-end (backend `curl` pass, then the frontend smoke
  test) against a freshly reseeded database and confirm every SC-00x in spec.md still holds.
- [ ] T031 Commit with the milestone-specific message required by the constitution and push.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup — blocks every user story.
- **US1 (Phase 3)** / **US2 (Phase 4)** / **US3 (Phase 5)**: each depends only on Foundational; not
  on each other. Build in any order — this doc does P1 → P1 → P1 in milestone-doc order.
- **US4 (Phase 6)**: depends on all three of US1-3's placeholder pages/endpoints existing (T026-T029
  reference them directly).
- **Polish (Phase 7)**: depends on all four stories.

### Parallel Opportunities

- T001-T004 (Setup) can all run in parallel — different files, no shared dependency.
- T009/T010 (frontend api + state modules) can run in parallel with each other and with T006-T008
  (backend), since they don't share a file.
- Within each story phase, the backend endpoint task and the frontend view task touch different
  files and could be split across two people, but the frontend view depends on the endpoint existing
  to be meaningfully testable — treat as sequential for a single implementer.

---

## Implementation Strategy

### MVP First

1. Setup → Foundational → US1 (Student).
2. **Stop and validate**: `quickstart.md` US1 section passes end-to-end, including the frontend
   register → login → land-on-`/student` flow.

### Incremental Delivery

US2 (Admin) → US3 (Company) → US4 (role enforcement, wiring everything together) → Polish, validating
at each checkpoint, then commit (T031).
