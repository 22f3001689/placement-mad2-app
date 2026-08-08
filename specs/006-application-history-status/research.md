# Research: Job Application History and Status Tracking

No `[NEEDS CLARIFICATION]` markers remain in spec.md — the three open design questions were
resolved directly with the user before the spec was written (see spec.md Assumptions). This
document records the resulting technical decisions.

## Decision: Status vocabulary is a data migration, not a schema migration

**Decision**: `Application.status` stays a `db.Column(db.String(20))` — no column type change.
Only the *set of valid values* changes, enforced at the route layer (a Python tuple), exactly
as today. A single Alembic data migration runs `UPDATE application SET status='interview' WHERE
status='waiting'` and `UPDATE application SET status='offer' WHERE status='selected'`.

**Rationale**: Matches this project's existing pattern (`JobPosition.status`, `Company.approval_status`
are also unconstrained strings validated at the API layer, per Milestone 1's decision documented
in VIVA_PREP.md/data-model.md history). No CHECK constraint exists today, so none needs to be
migrated.

**Alternatives considered**: A DB-level CHECK constraint or enum type — rejected as unnecessary
schema churn for a change this project has never made for any other status field, and SQLite's
enum support is weak enough that the app-layer tuple is already the project's established
validation point.

## Decision: Placed is terminal and auto-creates the Placement row synchronously

**Decision**: `POST /api/company/applications/<id>/decision` gains a guard: if the application's
current status is already `placed` or `rejected`, return 409 before making any change. When the
new status is `placed`, the request must include `position_title`, `salary`, and `joining_date`;
the route creates the `Placement` row in the same request/transaction as the status update.

**Rationale**: Per user decision, Placed is reached only by direct Company action — no separate
Student-side "accept offer" endpoint. Creating the Placement synchronously in the same request
avoids a whole class of "status says Placed but no Placement row exists yet" inconsistency that
a two-step or async flow would introduce, and needs no new infrastructure (no Celery/Redis exist
yet — those are Milestones 7-8).

**Alternatives considered**: A separate `POST /applications/<id>/place` endpoint just for the
Placed transition — rejected as an unnecessary second endpoint; the existing `decision` endpoint
already generalizes to any status with optional extra fields (it already does this for `remark`),
so extending it to accept placement fields when `status=placed` is the smaller change.

## Decision: Live approval gating is a query-time filter, not a cached/denormalized flag

**Decision**: `Company.approval_status == "approved"` is checked at query time on every
Student-facing read (`list_drives`, `get_drive`) and write (`apply_to_drive`) that touches a
`JobPosition`, exactly as `list_organizations`/`get_organization` already do for `Company` rows
directly. No new column, no cache, no background job.

**Rationale**: The gap is that `list_drives`/`get_drive`/`apply_to_drive` never joined through to
`Company.approval_status` at all (they only checked `JobPosition.status`) — the fix is adding
that join/filter, not introducing new infrastructure. SQLite easily handles this at demo scale.

**Alternatives considered**: Denormalizing an `is_visible` flag onto `JobPosition`, updated
whenever a Company's approval changes — rejected as premature optimization with no performance
problem to justify it, and it would require remembering to update it in `decide_company` (a new
failure mode this codebase doesn't need).

## Decision: Full Student-profile view for Admin is a new detail endpoint; for Company it's an extension of the existing one

**Decision**: Admin gets a new `GET /api/admin/students/<id>` returning the same profile shape
`student.py` already produces (`_profile_payload`) plus that Student's full application list —
Admin currently has no per-Student detail view at all. Company does **not** get a new endpoint;
`_application_detail_payload` (already used for the applicant-review screen) gains the two
fields it was missing (`graduation_year`, `contact`) — Company already views CGPA/branch/skills/photo/resume
one navigation step from an application, per Milestone 5.

**Rationale**: Minimizes new surface area — Company's existing "Review Application" screen
already satisfies FR-010's "one navigation step" success criterion once the two missing fields
are added; only Admin has a real gap (no student-detail view exists at all) that needs a new
endpoint.

**Alternatives considered**: A single shared `/students/<id>` endpoint reused by both Admin and
Company blueprints — rejected because Company's access must stay scoped ("any Student who has
applied to one of its drives," per FR-010), which is a materially different authorization rule
than Admin's ("any Student," per FR-009); duplicating a two-line payload function across two
already-separate blueprints is simpler than building a shared-but-differently-authorized route.
