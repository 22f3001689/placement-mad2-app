# Research: API Performance Optimization and Caching

No `[NEEDS CLARIFICATION]` markers remain in spec.md. This document records the technical
decisions made at plan time for the "how," building on the spec's "what."

## Decision: A small custom `app/cache.py`, not Flask-Caching

**Decision**: Implement a single decorator (`@cached_response(namespace, ttl=None)`) and a
single helper (`invalidate(namespace)`) directly against the `redis` client already installed
for Celery, rather than adding the `Flask-Caching` extension.

**Rationale**: This milestone's correctness requirement is precise, pattern-based invalidation
("delete every cached variant of listing X"), which needs a `SCAN`+`DELETE` over a key prefix.
Flask-Caching's `@cache.cached(query_string=True)` handles the read-through/TTL half well, but
its built-in invalidation is keyed by exact cache key (hashed from the full request), not by a
human-chosen namespace — bulk-invalidating "every variant of this listing" would need the same
kind of custom key-prefix scheme this plan builds directly, just underneath an extra layer of
abstraction. Writing ~40 lines directly against `redis` is simpler and more transparent than
configuring Flask-Caching to do the same thing.

**Alternatives considered**: `Flask-Caching` with a Redis backend — rejected per above.
`cachetools`/in-process memoization — rejected outright: it wouldn't be Redis (Principle I's
mandated stack explicitly names Redis for caching), and it wouldn't survive across the
multiple worker processes a real deployment would have.

## Decision: Cache keys are `cache:<namespace>:<raw query string>`, scoped per-endpoint by namespace

**Decision**: Four namespaces, one per target endpoint: `drives`, `orgs`, `admin_companies`,
`admin_students`. A request's cache key is `cache:<namespace>:<request.query_string>` (the raw,
unparsed query string bytes) — so `?q=python` and `?q=java` are automatically distinct keys,
and `?q=python` and `?status=ongoing&q=python` are also automatically distinct, with zero
custom parameter-parsing logic.

**Rationale**: The raw query string is already exactly the thing that determines a listing's
result set (per FR-002) — reusing it verbatim as the key differentiator needs no bespoke
canonicalization logic and can't drift out of sync with the route's own `request.args.get(...)`
reads.

**Alternatives considered**: Hashing the query string (e.g. `md5(query_string)`) — rejected as
an unnecessary indirection; raw query strings in this app are short (a handful of simple
filters), so there's no practical key-length concern that would justify hashing, and keeping
them human-readable makes `redis-cli KEYS 'cache:drives:*'` directly useful for debugging.

## Decision: Invalidation is namespace-wide (`SCAN` + `DELETE` on `cache:<namespace>:*`), not per-key

**Decision**: `invalidate(namespace)` deletes *every* cached entry under that namespace, not
just the specific query string that happened to be affected. `invalidate("drives")` after a
Company creates a Drive clears every previously-cached search/filter combination for the
Student drive listing, not just an empty-filter one.

**Rationale**: FR-004 explicitly requires this ("invalidate all cached variants of a listing
immediately," Edge Cases: "must invalidate every previously-cached variant... not just the
specific filter combination that happened to be viewed most recently"). A write can't know in
advance which cached filter combinations it affects, so the only correct move is to clear the
whole namespace.

**Alternatives considered**: Tracking which specific cache keys exist per namespace (e.g. a
Redis `SET` of active keys) to invalidate precisely — rejected as unneeded complexity; at this
app's scale, a `SCAN` over a few dozen keys on an infrequent write is effectively instant, and
maintaining a separate key-tracking structure would be more code with no measurable benefit.

## Decision: Every cache operation is wrapped so Redis errors fall back to the uncached path

**Decision**: `cached_response`'s read and write paths, and `invalidate()`, each catch
`redis.exceptions.RedisError` (the base class covering connection failures, timeouts, etc.),
log a warning, and continue as if the cache weren't there — a read-miss (falls through to the
live query) on a failed lookup, a no-op on a failed write, a no-op on a failed invalidation.
The client itself is constructed with a short (`socket_connect_timeout=2`) timeout so a down
Redis fails fast rather than hanging the request, mirroring Milestone 7's `broker_connection_timeout`
fix for the exact same class of problem.

**Rationale**: Directly satisfies FR-005/FR-006 and this project's constitution ("must degrade
gracefully or be mockable for local demo"). This is the same shape of fix Milestone 7 needed
for `.delay()` hanging when Redis was down — applying the lesson learned there up front instead
of re-discovering it.

**Alternatives considered**: Letting a Redis failure propagate as a `500` — rejected outright;
explicitly contradicts FR-005/FR-006 and the spec's User Story 3.

## Decision: A separate Redis logical DB index from Celery's broker

**Decision**: `CACHE_REDIS_URL` (default `redis://localhost:6379/1`) is distinct from
`REDIS_URL` (Celery's broker/backend, index `0`, unchanged from Milestone 7).

**Rationale**: Keeps cache keys and Celery's internal queue/result keys in entirely separate
keyspaces on the same running Redis instance — a `redis-cli -n 1 FLUSHDB` to clear the cache
during development can never accidentally wipe pending Celery messages, and vice versa.

**Alternatives considered**: Sharing index `0` with a `cache:` key prefix as the only
separation — rejected; a logical DB index is a stronger, free isolation boundary Redis already
provides, so there's no reason to rely on prefix discipline alone when a cleaner separation
costs nothing.
