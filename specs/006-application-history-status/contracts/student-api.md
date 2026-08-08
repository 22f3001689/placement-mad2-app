# Contract: `/api/student` changes

All existing endpoints keep their existing shape. The changes here are entirely about *which
rows are visible/actionable*, not new fields — except `GET /student/applications`, which gains
placement details.

## `GET /student/drives` (behavior change, same response shape)

Now also excludes drives whose owning Company is not currently `approved` (previously only
filtered `JobPosition.status == "ongoing"`).

## `GET /student/drives/<id>` (behavior change, same response shape)

Now responds `404` ("Drive not found") if the owning Company is not currently `approved` —
same as if the drive didn't exist, consistent with this project's existing cross-tenant 404
convention. Still has no `JobPosition.status` restriction (a closed drive stays viewable, per
Milestone 5's existing decision) — only the Company-approval check is new.

## `POST /student/drives/<id>/apply` (behavior change, same response shape)

Now responds `404` if the owning Company is not currently `approved`, in addition to the
existing `404` (drive doesn't exist) and `409` (already applied / drive completed) cases.

## `GET /student/applications` (changed payload only)

Adds one field to the existing per-application response: `placement`, `null` unless that
application's status is `placed`, in which case:
```json
"placement": {
  "position_title": "string",
  "salary": "integer or null",
  "joining_date": "ISO date or null"
}
```
