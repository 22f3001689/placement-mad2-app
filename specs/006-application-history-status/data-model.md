# Data Model: Job Application History and Status Tracking

No new tables and no column additions/removals. One column's valid *values* change, and one
existing-but-never-populated table (`Placement`) gets a real write path.

## `Application` (existing table, `app/models.py`)

| Column | Change |
|---|---|
| `status` | Valid values change from `applied/shortlisted/waiting/selected/rejected` to `applied/shortlisted/interview/offer/rejected/placed`. Column type/nullability unchanged (`String(20)`, `nullable=False`, `default="applied"`). |
| *(all other columns)* | Unchanged. |

**State transitions** (enforced at the route layer, in `company.py`'s `decide_application`):

```
applied → shortlisted → interview → offer → placed   (terminal)
   \          \            \           \
    \----------\------------\-----------\----------→ rejected  (terminal)
```

- `applied` is the only entry state (set automatically by `apply_to_drive`).
- `placed` and `rejected` are terminal — no further status change is accepted once reached.
- Any non-terminal status may move to `rejected` directly (a Company doesn't have to walk
  through every intermediate status before rejecting).
- Non-terminal statuses may also move backward or sideways (e.g. `offer` → `shortlisted`) —
  the spec does not require strictly forward-only progression, only that terminal states stay
  terminal (FR-002/FR-003).

**Data migration** (one-time, Alembic `upgrade()`):

```sql
UPDATE application SET status = 'interview' WHERE status = 'waiting';
UPDATE application SET status = 'offer'     WHERE status = 'selected';
```

`downgrade()` reverses this by mapping `interview` → `waiting` and `offer` → `selected` — an
approximation (some post-migration `interview` rows may originally have come from `applied`
via a new transition), acceptable because `downgrade()` is a dev-convenience path, never used
in the milestone submission itself.

## `Placement` (existing table, `app/models.py`) — now written by the app, not just the seed script

No column changes. New write path: created inside `decide_application` when `status="placed"`,
populated from the request body (`position_title`, `salary`, `joining_date`) plus
`student_id`/`company_id` (from the application being decided) and `application_id` (the
application itself, satisfying the existing `unique=True` constraint — one Placement per
Application).

## No changes to: `User`, `Company`, `Branch`, `Skill`, `student_skill`, `JobPosition`

`JobPosition`'s existing `status` (`ongoing`/`completed`) is untouched — that vocabulary is
unrelated to `Application.status` and this milestone doesn't touch it.
