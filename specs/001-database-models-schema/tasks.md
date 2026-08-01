# Tasks: Database Models & Schema

**Input**: Design documents from `specs/001-database-models-schema/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not included — research.md records the decision to verify manually via `quickstart.md`
instead of adding a test framework the reused reference project (`../hms-app-main`) doesn't have.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US4, from spec.md)
- All models for this milestone live in one file (`app/models.py`), so most tasks are sequential —
  edits to the same file can't safely run in parallel.

## Phase 1: Setup

**Purpose**: Flask app skeleton, config, and migration tooling — nothing story-specific yet.

- [ ] T001 Create the Flask app package skeleton in `app/__init__.py`: `create_app()` factory plus
  `db` (SQLAlchemy), `login` (LoginManager), `migrate` (Migrate) extension objects — copy the pattern
  from `../hms-app-main/app/__init__.py` (blueprint registration can stay empty/commented until
  Milestone 2 adds routes).
- [ ] T002 [P] Create `config.py`: `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI` = `sqlite:///app.db`,
  `SQLALCHEMY_TRACK_MODIFICATIONS = False` — copy from `../hms-app-main/config.py`.
- [ ] T003 [P] Create `requirements.txt` pinning Flask, Flask-SQLAlchemy, Flask-Migrate,
  Flask-Login, Werkzeug at the same versions used in `../hms-app-main/requirements.txt`.
- [ ] T004 Fix the `db-seed` Makefile target: it currently runs three `../hms-app-main`-specific
  seed scripts (`seed_doctor_details.py`, `seed_patel_data.py`) that don't exist in this repo — point
  it at `data-seeds/seed_data.py` only.
- [ ] T005 Run `flask db init` to create the `migrations/` folder (depends on T001, T002).

**Checkpoint**: `flask shell` boots without errors; `migrations/` exists.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The one model every user story depends on — nothing story-specific can start before this.

- [ ] T006 Create `app/models.py` with the `User` model: `id`, `username` (unique), `password_hash`,
  `role` (`admin`/`company`/`student`), `is_active` (default True), `created_at`,
  `set_password()`/`check_password()` (Werkzeug hashing), `UserMixin`, plus the
  `login.user_loader` callback — depends on T001.
- [ ] T007 Generate and apply the initial migration for the `users` table:
  `flask db migrate -m "add users table"` then `flask db upgrade` — depends on T005, T006.

**Checkpoint**: `users` table exists in `app.db`; a `User` row can be created and queried directly.

---

## Phase 3: User Story 1 - Admin exists the moment the app is set up (Priority: P1) 🎯 MVP

**Goal**: Exactly one Admin account exists after the one-time setup/seed step, with no code path able
to create a second one.

**Independent Test**: Wipe `app.db`, run the seed step, confirm exactly one `role="admin"` user exists;
run it again and confirm still exactly one.

### Implementation for User Story 1

- [ ] T008 [US1] Create `data-seeds/seed_data.py` with a `seed_database()` that drops/recreates all
  tables (`db.drop_all(); db.create_all()`) and inserts exactly one `User(role="admin")` — copy the
  idempotent-reseed pattern from `../hms-app-main/data-seeds/seed_data.py` — depends on T007.
- [ ] T009 [US1] Verify per `quickstart.md` → "Seed and check the Admin invariant": run
  `make db-seed` twice via the fixed target, confirm
  `User.query.filter_by(role="admin").count() == 1` both times — depends on T004, T008.

**Checkpoint**: User Story 1 is fully functional and independently demoable (SC-001).

---

## Phase 4: User Story 2 - Every person has exactly one role and one profile (Priority: P1)

**Goal**: Company and Student accounts each have their role-specific profile, correctly linked to
their `User` row.

**Independent Test**: Create a Company user + Company profile and a Student user + Student profile
directly against the schema; look up each profile's fields via a single hop from `User`.

### Implementation for User Story 2

- [ ] T010 [US2] Add the `Company` model to `app/models.py`: `user_id` (FK → User, unique),
  `company_name`, `industry`, `location`, `hr_contact`, `website`, `approval_status`
  (default `pending`), `created_at`, with a `User.company_profile` relationship — depends on T007.
- [ ] T011 [US2] Add the `Student` model to `app/models.py`: `user_id` (FK → User, unique), `name`,
  `branch`, `graduation_year`, `cgpa`, `skills`, `resume_path`, `contact`, `created_at`, with a
  `User.student_profile` relationship — depends on T010 (same file).
- [ ] T012 [US2] Generate and apply the migration for `company` and `student` tables:
  `flask db migrate -m "add company and student profiles"` then `flask db upgrade` — depends on T011.
- [ ] T013 [US2] Extend `data-seeds/seed_data.py`: seed one approved `Company` and one `Student`,
  each with fully populated profile fields — depends on T008, T012.
- [ ] T014 [US2] Verify per `quickstart.md` → "Check role-specific profiles round-trip" — depends on
  T013.

**Checkpoint**: User Stories 1 and 2 both work independently (SC-002).

---

## Phase 5: User Story 3 - A Company's job posting and its applicants can be traced (Priority: P2)

**Goal**: A Job Position (Placement Drive) belongs to one Company; an Application links one Student
to one Job Position and can't be duplicated for the same pair.

**Independent Test**: Create a Company → JobPosition → Student → Application chain; confirm the
Application is reachable from both sides, and a second identical Application fails.

### Implementation for User Story 3

- [ ] T015 [US3] Add the `JobPosition` model to `app/models.py`: `company_id` (FK → Company),
  `title`, `description`, `eligible_branches`, `min_cgpa`, `eligible_graduation_year`, `salary`,
  `skills_required`, `application_deadline`, `status` (default `pending`), `created_at`, with a
  `Company.job_positions` relationship — depends on T012.
- [ ] T016 [US3] Add the `Application` model to `app/models.py`: `student_id` (FK → Student),
  `job_position_id` (FK → JobPosition), `application_date` (default now), `status`
  (default `applied`), `UniqueConstraint(student_id, job_position_id)`, with
  `Student.applications` / `JobPosition.applications` relationships — depends on T015 (same file).
- [ ] T017 [US3] Generate and apply the migration for `job_position` and `application` tables,
  including the unique constraint — depends on T016.
- [ ] T018 [US3] Extend `data-seeds/seed_data.py`: seed one `JobPosition` for the seeded Company and
  one `Application` from the seeded Student to it — depends on T013, T017.
- [ ] T019 [US3] Verify per `quickstart.md` → "Check the duplicate-application guard": inserting a
  second `Application` for the same `(student_id, job_position_id)` raises `IntegrityError` on
  commit — depends on T018.

**Checkpoint**: User Stories 1–3 all work independently (SC-003).

---

## Phase 6: User Story 4 - A completed placement is recorded permanently (Priority: P3)

**Goal**: A `Placement` is its own durable record, readable even after the originating Company is
deactivated or Job Position closed.

**Independent Test**: Take a Selected Application, create a Placement from it, deactivate the
Company / close the Job Position, and confirm the Placement is still fully readable.

### Implementation for User Story 4

- [ ] T020 [US4] Add the `Placement` model to `app/models.py`: `student_id` (FK → Student),
  `company_id` (FK → Company), `application_id` (FK → Application, unique, nullable),
  `position_title` (snapshot string), `salary`, `joining_date`, `created_at`, with a
  `Student.placements` relationship — depends on T016.
- [ ] T021 [US4] Generate and apply the migration for the `placement` table — depends on T020.
- [ ] T022 [US4] Extend `data-seeds/seed_data.py`: set the seeded Application's status to `selected`
  and create the matching `Placement` row — depends on T018, T021.
- [ ] T023 [US4] Verify per `quickstart.md` → "Check history survives deactivation/closure" —
  depends on T022.

**Checkpoint**: All four user stories work independently (SC-004).

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T024 [P] Add a `__repr__` to `Company`, `Student`, `JobPosition`, `Application`, and
  `Placement`, matching the style already used on `User`, for readable `flask shell` debugging.
- [ ] T025 Re-run the full `quickstart.md` against a freshly reseeded database end-to-end and
  confirm every SC-00x check in spec.md still passes (SC-005: whole schema rebuilds from code only).
- [ ] T026 Commit with the milestone-specific message required by the constitution (e.g.
  `Milestone-1 PPA-V2 Database-Models-Schema`) and push.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup — blocks every user story.
- **US1 (Phase 3)**: depends on Foundational only. This is the MVP slice.
- **US2 (Phase 4)**: depends on Foundational; extends the same seed script as US1 (T013 depends on
  T008), so in practice do US1 before US2.
- **US3 (Phase 5)**: depends on US2's `Company`/`Student` tables existing (T015 depends on T012) and
  its seed data (T018 depends on T013).
- **US4 (Phase 6)**: depends on US3's `Application` table (T020 depends on T016) and seed data
  (T022 depends on T018).
- **Polish (Phase 7)**: depends on all four stories being complete.

Because every story adds to the same `app/models.py` and the same `data-seeds/seed_data.py`, the
stories are logically independent (each is separately verifiable) but not executable out of order —
build them P1 → P1 → P2 → P3 as listed.

### Parallel Opportunities

- T002 and T003 (different files: `config.py`, `requirements.txt`) can run in parallel.
- T024 touches five models but is otherwise independent polish — safe to do any time after Phase 6.
- No other tasks are parallelizable: everything else edits `app/models.py` or
  `data-seeds/seed_data.py` in sequence.

---

## Implementation Strategy

### MVP First

1. Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1).
2. **Stop and validate**: run the two `make db-seed` calls from T009, confirm the Admin invariant.
3. That alone is a demoable, working slice of Milestone 1.

### Incremental Delivery

Phase 4 (US2) → Phase 5 (US3) → Phase 6 (US4) → Phase 7 (Polish), validating at each checkpoint
per the quickstart.md section named in that phase's verify task, then commit (T026) once all four
stories and polish are done.
