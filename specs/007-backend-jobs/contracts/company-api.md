# Contract: `/api/company` additions

All new endpoints are `company_approved_required`, same as every existing Company endpoint.

## `POST /company/exports` (new)

Creates a `csv_export` job for the current Company (covering its own applications/placements)
and enqueues it on Celery. Same response/error shape as the Student version.

## `GET /company/exports` / `GET /company/exports/<id>` (new)

Same shape and ownership rules as the Student version (`student-api.md`), scoped to the current
Company's own jobs.

## `GET /company/reports` (new)

Lists the current Company's own system-generated `placement_report` jobs (most recent first) —
these are created by the Celery Beat job, never by a direct POST from the Company.

**Response** (200): array of `{id, status, download_url, period_start, period_end, completed_at}`.

## `GET /company/reports/<id>` (new)

Single report job's status/detail, same ownership rules (`404` if not this Company's).
