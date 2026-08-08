# Contract: `/api/student` additions

All new endpoints are `role_required(ROLE_STUDENT)`, same as every existing Student endpoint.

## `POST /student/exports` (new)

Creates a `csv_export` job for the current Student and enqueues it on Celery. Returns
immediately, before the export runs.

**Response** (202):
```json
{"id": 1, "job_type": "csv_export", "status": "pending", "created_at": "..."}
```

`503` if Redis/Celery is unreachable when enqueuing (`{"error": "Export could not be scheduled - background jobs are unavailable"}`), so a broken worker fails clearly instead of silently hanging.

## `GET /student/exports` (new)

Lists the current Student's own export jobs (most recent first) — never another user's.

**Response** (200): array of `{id, job_type, status, download_url, created_at, completed_at}` —
`download_url` is `null` until `status="ready"`.

## `GET /student/exports/<id>` (new)

Single job's status, same shape as one list item. `404` if the job doesn't exist or isn't owned
by the current Student (same cross-tenant-404 convention as every other endpoint in this app).
