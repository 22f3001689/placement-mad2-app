# Quickstart: API Performance Optimization and Caching

Assumes Redis is already running (`make redis-up`, from Milestone 7) and the app is seeded.

## Scenario 1: repeated search is faster (US1)

1. `time curl -s -b <admin-cookie-jar> "http://localhost:5000/api/admin/students?q=john"` — note the time.
2. Run the exact same command again immediately — confirm it's faster and returns identical JSON.
3. Run it with a different `?q=` value — confirm it's treated as a separate (initially slower) request, not served from the first query's cache.
4. Repeat for `GET /api/student/drives`, `GET /api/student/organizations`, `GET /api/admin/companies`.

## Scenario 2: a write is always visible immediately, never masked by cache (US2)

1. As a Student, `GET /api/student/drives` (warms the `drives` cache).
2. As the owning Company, create a new Drive.
3. Immediately repeat step 1 — confirm the new Drive appears, not the stale cached list.
4. As Admin, `GET /api/admin/companies` (warms `admin_companies`); as Admin, approve or reject a pending Company; repeat the `GET` — confirm the new `approval_status` appears immediately. Also repeat `GET /api/student/organizations` and `GET /api/student/drives` — confirm the approval change is visible there too (per the invalidation map).
5. As Admin, `GET /api/admin/students` (warms `admin_students`); toggle a Student's active status; repeat the `GET` — confirm it's reflected immediately.
6. As that Student, update their profile (e.g. change `name`); as Admin, repeat `GET /api/admin/students` — confirm the new name appears immediately.

## Scenario 3: graceful degradation (US3)

1. `make redis-down`.
2. Repeat every request in Scenarios 1-2 — confirm every one still returns correct, current data (just without the speed benefit).
3. Confirm an unrelated feature (login, applying to a Drive) is completely unaffected.
4. `make redis-up` to restore.

## Verifying the safety-net TTL

1. Warm a cache entry, then wait longer than `CACHE_DEFAULT_TTL` (default 60s) without performing any write.
2. Confirm `redis-cli -n 1 KEYS 'cache:*'` no longer shows that key (expired on its own, per FR-003).
