# Phase 0 Research: Admin Dashboard & Management

No open `[NEEDS CLARIFICATION]` markers were left in the spec — the decisions below resolve every
technical unknown the Technical Context flagged.

## Decision: "Remove" is a status change, not a row deletion

- **Decision**: Company approval and Job Posting approval both become a "decision" action that writes
  `"approved"` or `"rejected"` into the existing `approval_status`/`status` columns. Nothing in this
  milestone runs `db.session.delete()` on a `Company` or `JobPosition`.
- **Rationale**: See spec.md's Assumptions — Milestone 1's data model deliberately has no cascading
  delete from `Application`/`Placement` up to `JobPosition`/`Company`, specifically so that history
  survives. A real delete here would either orphan those child rows or force adding the exact cascade
  behavior Milestone 1 rejected. Reusing the status column is also less code than a delete path would
  be.
- **Alternatives considered**: Hard delete with cascading cleanup — rejected, contradicts Milestone 1's
  explicit design intent and adds destructive-action complexity (confirmation flows, cascade rules)
  the milestone doc's actual wording doesn't require.

## Decision: One "decision" endpoint per entity, not separate approve/reject routes

- **Decision**: `POST /api/admin/companies/<id>/decision` and
  `POST /api/admin/job-positions/<id>/decision`, each taking `{"status": "approved" | "rejected"}` in
  the body, instead of four separate `/approve` and `/reject` routes.
- **Rationale**: Both actions are the same operation (write a status, validate it's an allowed value) —
  one route with a validated enum body is less code than two near-identical routes, and it directly
  supports FR-005's requirement to let Admin change a decision again later without needing a third
  route.
- **Alternatives considered**: Separate `/approve` and `/reject` routes per entity (four total) —
  rejected as needless duplication for what's a one-line difference in behavior.

## Decision: One "toggle-active" endpoint, not separate deactivate/reactivate routes

- **Decision**: `POST /api/admin/users/<id>/toggle-active` flips `User.is_active`, mirroring
  `../hms-app-main/app/routes/admin.py`'s `blacklist_doctor`/`blacklist_patient` pattern
  (`user.is_blacklisted = not user.is_blacklisted`) exactly, adapted to this project's `is_active`
  column and JSON response instead of a flash-redirect.
- **Rationale**: Same operation either direction (flip a boolean); a toggle is simpler than tracking
  "which direction" client-side and calling two different routes. The endpoint returns the resulting
  `is_active` value so the frontend always shows the true state without a second request.
- **Alternatives considered**: Separate `/deactivate` and `/reactivate` routes — rejected as the same
  unnecessary duplication as the approve/reject case above.

## Decision: Substring search via SQLAlchemy `ilike`, reusing the reference project's approach

- **Decision**: Company search matches `company_name`/`industry`; Student search matches
  `name`/`user.username` (used as the "ID" the spec refers to, since Student has no separate ID field
  visible to Admin beyond its username and primary key)/`contact`. All via `or_(...ilike(f"%{q}%"))`,
  the same construct `../hms-app-main/app/routes/admin.py` uses for its doctor/patient search.
- **Rationale**: Directly reusable pattern (constitution Principle IV); `ilike` gives case-insensitive
  substring matching with zero extra dependency, which is all FR-008/FR-009 ask for.
- **Alternatives considered**: A dedicated full-text search (e.g. SQLite FTS5) — rejected as disproportionate
  to a "substring match" requirement with no stated dataset-size problem to justify it.

## Decision: The Admin-facing "view all" endpoints double as the approval queues

- **Decision**: `GET /api/admin/job-positions` and `GET /api/admin/companies` both accept an optional
  `status` query parameter; omitting it returns every row (User Story 5's "view all"), passing
  `status=pending` returns just the approval queue (User Story 2/3). No separate "pending queue"
  endpoint exists.
- **Rationale**: It's the same underlying query with one more `WHERE`, not two different capabilities —
  building a second endpoint would duplicate the row-shaping code for no behavioral gain.
- **Alternatives considered**: Separate `/companies/pending` and `/companies` endpoints — rejected as
  the same needless duplication called out in the decision-endpoint and toggle-endpoint choices above.
