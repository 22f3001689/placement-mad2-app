# Implementation Plan: API Performance Optimization and Caching

**Branch**: `008-api-caching` | **Date**: 2026-08-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-api-caching/spec.md`

## Summary

Add a thin, Redis-backed response cache for the four read-heavy listing endpoints named in
the milestone (Student job/drive listings, Student company search, Admin company search,
Admin student search), keyed by endpoint + exact query string, with a short TTL as a safety
net and explicit invalidation on every write that can change what one of these listings
would show. No new dependency — reuses the `redis` package already installed for Celery
(Milestone 7), on a separate logical Redis DB index so cache keys never collide with Celery's
broker/queue keys. No API response shape changes; this is purely a transparent performance
layer with an explicit correctness contract (see `contracts/invalidation-map.md`).

## Technical Context

**Language/Version**: Python 3.11 (Flask) — same as all prior milestones

**Primary Dependencies**: `redis` (already installed, Milestone 7) — no new dependency

**Storage**: Redis, same instance as Celery's broker (Milestone 7's `docker-compose.yml` service), logical DB index 1 (`CACHE_REDIS_URL`, defaults to `redis://localhost:6379/1`) vs. Celery's index 0, so a `FLUSHDB`/key-pattern operation on one never touches the other

**Testing**: Manual verification via `curl` timing comparisons and write-then-read sequences, per this project's established convention

**Target Platform**: Same local dev environment as Milestone 7 (Redis via Docker, already running)

**Project Type**: Existing Flask app, no new process (unlike Celery, caching is inline in the request path, not a background worker)

**Performance Goals**: Second-and-later identical requests to a cached listing must be measurably faster than the first (cache hit avoids the SQL query and payload rebuild entirely)

**Constraints**: Every write listed in FR-004 must invalidate every cached variant of the listing(s) it affects, not just one filter combination; a cache failure (unavailable or erroring mid-request) must never surface to the caller — every affected route must behave exactly as if there were no cache at all

**Scale/Scope**: One new module (`app/cache.py`), one decorator applied to 4 existing view functions, one invalidation call added at each of 4 existing write call sites, 2 new config values, no schema changes, no new endpoints, no frontend changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Mandated stack (Redis for caching)**: PASS — this milestone is exactly the "Redis (caching)" slice of Principle I's mandated stack, previously unused.
- **"Caching MUST be applied to hot read endpoints... with explicit cache expiry/invalidation — stale reads after a write are a bug"** (Data & Access Constraints): PASS — this is this plan's central design constraint; see `contracts/invalidation-map.md` for the explicit write→invalidate mapping.
- **Local-demo-first, graceful degradation**: PASS — every cache operation is wrapped so a Redis failure falls back to the uncached path silently; verified the same way Milestone 7's `make redis-down` check was.
- **Reuse before rebuild**: PASS — reuses the `redis` package and the running Redis container from Milestone 7 rather than adding Flask-Caching or a second cache technology; `../hms-app-main` has no caching precedent to reuse from (confirmed by inspection during Milestone 7 planning).
- **Simple/Human/Surgical**: PASS — one small decorator + one small invalidation helper, applied at exactly the call sites the spec names; no generic cache framework, no cache warming, no cache preloading — none of which the milestone asks for.

No violations; Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/008-api-caching/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── invalidation-map.md
└── tasks.md              # /speckit-tasks output, not created here
```

### Source Code (repository root)

```text
app/
├── cache.py                    # new: @cached_response(namespace, ttl?) decorator,
│                                 #      invalidate(namespace) helper, lazy Redis client
├── routes/
│   ├── student.py                # list_drives, list_organizations get @cached_response;
│   │                              # apply_to_drive/update_profile call invalidate(...)
│   ├── admin.py                  # list_companies, list_students get @cached_response;
│   │                              # decide_company/toggle_active call invalidate(...)
│   └── company.py                # create_drive/complete_drive call invalidate(...)
config.py                        # + CACHE_REDIS_URL, CACHE_DEFAULT_TTL
.env.example                      # + CACHE_REDIS_URL placeholder
```

**Structure Decision**: No new process, no new blueprint — caching is added as a decorator on
existing view functions and a helper called from existing write handlers, in the same files
those already live in. This matches how every other cross-cutting concern in this app
(logging, decorators) is layered on top of existing routes rather than restructuring them.

## Complexity Tracking

Not applicable — no Constitution Check violations.
