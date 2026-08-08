# Feature Specification: API Performance Optimization and Caching

**Feature Branch**: `008-api-caching`

**Created**: 2026-08-08

**Status**: Draft

**Input**: User description: "Milestone 8: API Performance Optimization and Caching Using Redis (Flask). Use Redis caching for API optimization, cache frequently used endpoints (job listings, company search, student search), implement proper cache expiry and refresh policies. Target endpoints: GET /student/drives (job listings), GET /student/organizations (company search, Student-facing), GET /admin/companies (company search, Admin-facing), GET /admin/students (student search, Admin-facing). Must satisfy 'stale reads after a write are a bug' - writes that affect a cached listing's results must explicitly invalidate the relevant cached entries, not just rely on TTL expiry. Must degrade gracefully if the cache is unavailable."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Repeated searches return instantly instead of re-querying every time (Priority: P1)

A Student browsing job listings, or an Admin searching Companies/Students, repeats the same or similar search multiple times in a short session (paging back, re-checking a filter). The system should serve the repeat request noticeably faster than the first one, without doing the same expensive lookup again.

**Why this priority**: This is the entire point of the milestone — every other requirement (invalidation, degradation) exists in service of this being safe to do.

**Independent Test**: Issue the same search request twice in a row and confirm the second response is measurably faster and returns identical results to the first, with no visible difference in behavior to the caller.

**Acceptance Scenarios**:

1. **Given** a Student requests job listings with a given filter/search term, **When** they issue the identical request again shortly after, **Then** the second response returns the same results faster than the first.
2. **Given** an Admin searches Companies or Students with a given term, **When** they repeat that exact search, **Then** the second response is faster and identical in content.
3. **Given** two different search terms or filters, **When** each is requested, **Then** each is treated and stored as a distinct result set — one search's cached result is never returned for a different search.

---

### User Story 2 - A change is always visible immediately, never masked by a stale cached result (Priority: P1)

An action that changes what a listing would show — a Company posting or closing a Drive, an Admin approving/rejecting a Company, an Admin blacklisting/whitelisting a User, a Student updating their profile — must be reflected the very next time that listing is viewed, by anyone, even if that listing was cached moments before.

**Why this priority**: Equal priority to Story 1 — a fast but wrong answer is worse than a slow correct one. This is an explicit, non-negotiable correctness requirement, not a nice-to-have.

**Independent Test**: Warm a listing's cache by viewing it, perform a write that changes what it should show, then view the same listing again immediately (well within any time-based cache lifetime) and confirm the update is visible, not the stale cached version.

**Acceptance Scenarios**:

1. **Given** a cached Drive listing, **When** the owning Company creates a new Drive or marks one complete, **Then** the very next request for that listing reflects the change, not the previously cached snapshot.
2. **Given** a cached Company search result, **When** an Admin approves or rejects a Company, **Then** the very next Company search reflects the new approval state.
3. **Given** a cached Student search result, **When** an Admin toggles a User's active status, **Then** the very next Student search reflects the new status.
4. **Given** a cached listing that includes a Student's own profile details, **When** that Student updates their profile, **Then** the very next relevant search/listing reflects the update.
5. **Given** no write has occurred, **When** enough time passes, **Then** a cached result eventually expires on its own (a safety net independent of explicit invalidation, in case some future write path is missed).

---

### User Story 3 - The application keeps working normally if the cache is unavailable (Priority: P2)

If the caching layer is down or unreachable, every affected listing must still work — just without the speed benefit — and nothing else in the application should be affected at all.

**Why this priority**: Lower than Stories 1-2 because it's a resilience property, not a feature anyone actively uses — but it's a hard requirement per this project's local-demo-first principle (no feature may introduce a new way for the whole app to break).

**Independent Test**: Make the cache unavailable, then exercise every cached listing and confirm each still returns correct, current results (just without a speed benefit), and confirm no unrelated feature is affected.

**Acceptance Scenarios**:

1. **Given** the cache is unavailable, **When** a Student requests job listings, **Then** they still receive correct, current results.
2. **Given** the cache is unavailable, **When** an Admin searches Companies or Students, **Then** they still receive correct, current results.
3. **Given** the cache is unavailable, **When** any unrelated feature (login, applying to a drive, viewing a profile, etc.) is used, **Then** it is completely unaffected.

### Edge Cases

- Two different filters/search terms on the same listing (e.g. different `q=` values, different status filters) must never be confused with each other — each distinct combination of parameters is cached and invalidated independently.
- A write action must invalidate every previously-cached variant of a listing it affects, not just the specific filter combination that happened to be viewed most recently.
- If the cache store itself errors out mid-request (not just "unavailable at startup" but a failure partway through), the request must still complete successfully with correct data, exactly as if there had been no cache at all.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST cache the results of the following frequently-used read operations: Student-facing job/drive listings, Student-facing company search, Admin-facing company search, and Admin-facing student search.
- **FR-002**: The system MUST treat different search terms/filters on the same listing as independent cache entries — never returning one filter combination's cached result for a different one.
- **FR-003**: Every cached entry MUST have a time-based expiry, so a result is never served indefinitely even if no relevant write is ever detected.
- **FR-004**: The system MUST explicitly invalidate all cached variants of a listing immediately when a write occurs that would change that listing's results, rather than relying solely on time-based expiry — specifically: Company drive creation/completion (affects job/drive listings), Admin company approval/rejection (affects company search), Admin user active-status toggling (affects student search, for Students), Student profile updates (affects any listing exposing that Student's profile data).
- **FR-005**: The system MUST continue to serve correct, current results for every cached listing if the cache store is unavailable or errors, with no user-visible failure.
- **FR-006**: A failure in the caching layer MUST NOT affect any feature outside the specific listings being cached.

### Key Entities

- **Cached search/listing result**: A stored snapshot of a specific listing request (identified by which listing plus its exact filter/search parameters), with a defined lifetime, that can be explicitly invalidated by a relevant write.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A repeated identical search on any of the four target listings returns measurably faster on the second and subsequent requests than on the first, with identical results.
- **SC-002**: 100% of tested write-then-read sequences (per Edge Cases and User Story 2's scenarios) show the read reflecting the write immediately — zero observed stale reads across repeated testing.
- **SC-003**: With the cache store unavailable, 100% of requests to the four target listings still succeed with correct, current data, and zero other features are affected.

## Assumptions

- The cache store is Redis, already running locally (introduced in Milestone 7 for background jobs), reused here on a separate logical database index to avoid any key collision with Celery's use of Redis as a broker.
- A short, fixed time-based expiry (on the order of a minute) is used as the safety-net expiry for every cached entry, per FR-003 — the specific number is a technical/plan-level detail, not a product decision.
- "Frequently used" is interpreted per the milestone's own explicit list (job listings, company search, student search) rather than a broader performance audit of every endpoint in the app — matching this milestone's stated 3-day scope.
