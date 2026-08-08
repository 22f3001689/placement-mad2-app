# Data Model: Backend Jobs

## `User` (existing table, `app/models.py`) — one new column

| Column | Change |
|---|---|
| `email` | New: `String(255)`, `unique=True`, `nullable=True` at the DB level (SQLite/migration constraint), enforced as required by the API layer for all new registrations. Backfilled for existing rows via the migration (see research.md). |

## `Application` (existing table) — one new column

| Column | Change |
|---|---|
| `interview_reminded_at` | New: `DateTime`, `nullable=True`. Set (once) the first time a reminder email is sent for that Application's `interview_datetime`. `NULL` = not yet reminded. |

## `EmailTemplate` (new table)

| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK | |
| `key` | String(50), unique, not null | e.g. `interview_reminder`, `export_ready`, `report_ready` |
| `subject` | String(200), not null | `str.format()` placeholders allowed |
| `body` | Text, not null | `str.format()` placeholders allowed |

Seeded rows (like `Branch`/`Skill`), not user-editable via any UI in this milestone:

| `key` | Placeholders used |
|---|---|
| `interview_reminder` | `{student_name}`, `{company_name}`, `{job_title}`, `{interview_datetime}` |
| `export_ready` | `{name}`, `{download_url}` |
| `report_ready` | `{company_name}`, `{download_url}`, `{period_start}`, `{period_end}` |

## `ExportJob` (new table)

| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK | |
| `user_id` | Integer, FK → `users.id`, not null | Owning User — for a `placement_report`, this is the Company's `user_id` |
| `job_type` | String(20), not null | `csv_export` \| `placement_report` |
| `status` | String(20), not null, default `pending` | `pending` \| `running` \| `ready` \| `failed` |
| `file_path` | String(255), nullable | Relative path under `app/static/exports/` or `app/static/reports/`, set when `status="ready"` |
| `period_start` | Date, nullable | Only meaningful for `placement_report` |
| `period_end` | Date, nullable | Only meaningful for `placement_report` |
| `error_message` | Text, nullable | Set when `status="failed"` |
| `created_at` | DateTime, default now | |
| `completed_at` | DateTime, nullable | Set when `status` becomes `ready` or `failed` |

**Relationships**: `ExportJob.user` → `User` (plain FK, no cascade — a job record persists even
if unrelated data changes; no cascading delete concern since `User` rows are never deleted in
this app, only deactivated).

**State transitions**: `pending` → `running` → `ready` (terminal) or `failed` (terminal). No
other transitions are valid; the task itself drives every transition, never a user action.

## No changes to: `Company`, `Student`, `Branch`, `Skill`, `student_skill`, `JobPosition`,
`Placement`

`Placement`'s existing shape already carries everything a placement report needs
(`position_title`, `salary`, `joining_date`) — the report job reads it, doesn't change it.
