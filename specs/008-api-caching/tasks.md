# Tasks: API Performance Optimization and Caching

**Input**: Design documents from `/specs/008-api-caching/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/invalidation-map.md, quickstart.md

**Tests**: Not requested for this milestone (project convention: manual verification via quickstart.md).

**Organization**: Tasks are grouped by user story (US1-US3, per spec.md).

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [ ] T001 Confirm Redis is running (`docker ps | grep redis`, or `make redis-up`); confirm on branch `feat/milestone-8-api-caching` off latest `main`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The cache module and config every user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 Add `CACHE_REDIS_URL` (default `redis://localhost:6379/1`) and `CACHE_DEFAULT_TTL` (default `60`) to `config.py`, following the existing `REDIS_URL`/`MAIL_*` pattern (`os.environ.get(...)`)
- [ ] T003 [P] Add `CACHE_REDIS_URL` to `.env.example` with a placeholder/default value and a one-line comment noting it's a separate DB index from Celery's `REDIS_URL`
- [ ] T004 Create `app/cache.py`: a lazily-constructed module-level Redis client (`redis.Redis.from_url(CACHE_REDIS_URL, socket_connect_timeout=2, socket_timeout=2)`), the `@cached_response(namespace, ttl=None)` decorator (reads `cache:<namespace>:<request.query_string>`; on hit, returns a `Response` built from the cached bytes with `mimetype="application/json"`; on miss, calls the view, normalizes its return value via `current_app.make_response(...)`, caches the body if `status_code == 200`, returns the response), and `invalidate(namespace)` (`SCAN`+`DELETE` over `cache:<namespace>:*`) — every Redis call wrapped in `try/except redis.exceptions.RedisError`, logged via `get_logger(__name__)`, falling back to the uncached path per research.md
- [ ] T005 Manually verify `app/cache.py` imports cleanly and a direct `cached_response`/`invalidate` round-trip works against the running Redis (e.g. via a `flask shell` snippet) before wiring it into any route

**Checkpoint**: `app/cache.py` is a working, independently-testable module. No route behavior has changed yet.

---

## Phase 3: User Story 1 - Repeated searches return instantly (Priority: P1) 🎯 MVP

**Goal**: The four target listings are cached per exact query string with a TTL safety net.

**Independent Test**: Issue the same search twice, confirm the second is faster and identical; issue a different search, confirm it's treated independently.

### Implementation for User Story 1

- [ ] T006 [P] [US1] Apply `@cached_response("drives")` to `list_drives` in `app/routes/student.py`
- [ ] T007 [P] [US1] Apply `@cached_response("orgs")` to `list_organizations` in `app/routes/student.py`
- [ ] T008 [P] [US1] Apply `@cached_response("admin_companies")` to `list_companies` in `app/routes/admin.py`
- [ ] T009 [P] [US1] Apply `@cached_response("admin_students")` to `list_students` in `app/routes/admin.py`
- [ ] T010 [US1] Manually verify via quickstart.md Scenario 1 (repeated identical search faster with identical results; different search treated independently) for all four endpoints

**Checkpoint**: All four listings are cached and demonstrably faster on repeat. Not yet safe against stale reads after a write - that's US2.

---

## Phase 4: User Story 2 - Writes always invalidate affected caches (Priority: P1)

**Goal**: Every write in contracts/invalidation-map.md calls `invalidate(...)` for every namespace it affects, in the same request.

**Independent Test**: Warm a cache, perform each mapped write, confirm the very next read reflects it - zero stale reads.

### Implementation for User Story 2

- [ ] T011 [US2] In `app/routes/company.py`, call `invalidate("drives")` in `create_drive` and `complete_drive`, after the commit
- [ ] T012 [US2] In `app/routes/admin.py`, call `invalidate("admin_companies")`, `invalidate("orgs")`, and `invalidate("drives")` in `decide_company`, after the commit
- [ ] T013 [US2] In `app/routes/admin.py`, call `invalidate("admin_companies")` and `invalidate("admin_students")` in `toggle_active`, after the commit
- [ ] T014 [US2] In `app/routes/student.py`, call `invalidate("admin_students")` in `update_profile`, after the commit
- [ ] T015 [US2] Manually verify via quickstart.md Scenario 2 (all 5 write→read sequences from contracts/invalidation-map.md show the write reflected immediately, zero stale reads)

**Checkpoint**: User Stories 1 AND 2 both work independently - caching is now both fast and correct.

---

## Phase 5: User Story 3 - Graceful degradation if the cache is unavailable (Priority: P2)

**Goal**: Every cached endpoint keeps returning correct data if Redis is down or errors mid-request; nothing else in the app is affected.

**Independent Test**: Stop Redis, exercise all four cached endpoints and every write in the invalidation map, confirm everything still works correctly (just without the speed benefit), confirm unrelated features are unaffected.

### Implementation for User Story 3

- [ ] T016 [US3] Manually verify via quickstart.md Scenario 3: `make redis-down`, re-run Scenarios 1-2's requests, confirm every one still returns correct current data with no error, and confirm login/apply-to-drive/profile-view are unaffected; `make redis-up` to restore
- [ ] T017 [US3] Manually verify the TTL safety net independent of any write (quickstart.md's final section): warm a cache entry, wait past `CACHE_DEFAULT_TTL` with no write, confirm the key expired on its own via `redis-cli -n 1 KEYS 'cache:*'`

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T018 Run `make format` (ruff + black) across all touched backend files
- [ ] T019 Update `VIVA_PREP.md` (Tech Stack, a new Caching subsection referencing the invalidation map, Milestone Map) — stays untracked/gitignored, not part of the PR
- [ ] T020 Full manual regression: re-run quickstart.md Scenarios 1-3 end-to-end in one sitting after all tasks above are complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories (the cache module must exist and work before any route uses it)
- **User Stories (Phase 3-5)**: All depend on Foundational. US1 and US2 (both P1) are tightly coupled in practice (a decorator without invalidation is actively unsafe), so implement them together even though they're listed as separate stories for independent-test clarity. US3 (P2) is a verification-only phase - the graceful-degradation behavior is already built into `app/cache.py` from Foundational; this phase just proves it.
- **Polish (Phase 6)**: Depends on all three user stories being complete

### Parallel Opportunities

- T003 can proceed alongside T002 (different files).
- T006-T009 are all marked [P] - different route functions, independent of each other (though all depend on T004 being complete first).

---

## Implementation Strategy

### MVP First

Given how small this milestone is, US1 and US2 together (T006-T015) are the practical MVP -
shipping caching without invalidation would violate the constitution's explicit "stale reads
after a write are a bug" rule, so they should land as one unit rather than being staged.

1. Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. Complete Phase 3 + Phase 4 together (US1 + US2)
3. **STOP and VALIDATE**: Run quickstart.md Scenarios 1-2
4. Complete Phase 5 (US3) - verification only, confirms what Foundational already built
5. Complete Phase 6 (Polish)
