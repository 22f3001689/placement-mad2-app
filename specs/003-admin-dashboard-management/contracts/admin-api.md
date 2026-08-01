# Admin API Contract

Base path: `/api/admin`. All requests/responses are JSON. Every endpoint below requires an active
session with `role == "admin"` (the existing `role_required("admin")` decorator from Milestone 2) — no
active session is `401`, an active session with the wrong role is `403`, exactly as documented in
Milestone 2's contract.

## GET /api/admin/dashboard

Shown alongside "Welcome Admin" and the search bar in Section 1.

**Responses**:
- `200` —
  ```json
  { "students": 12, "companies": 5, "job_positions": 8, "applications": 23 }
  ```
  `companies` counts only `approval_status == "approved"` Companies — matching what Registered
  Companies actually lists. A pending or rejected Company isn't counted here, since it can't be
  logged in "as a Company" in the sense this total implies (it can't create Drives yet, or ever).

## GET /api/admin/companies

Backs both Registered Companies (`status=approved`) and Company Applications (`status=pending`).

**Query params** (both optional): `status` (`pending` | `approved` | `rejected`), `q` (substring match
on `company_name` or `industry` — used by Registered Companies' search, per research.md; Company
Applications never passes `q`).

**Responses**:
- `200` —
  ```json
  [
    {
      "id": 1,
      "user_id": 4,
      "username": "acme_corp",
      "company_name": "Acme Corp",
      "industry": "Software",
      "approval_status": "pending",
      "is_active": true
    }
  ]
  ```
  `user_id` is the id to pass to `POST /api/admin/users/<id>/toggle-active` — it's a `User` id,
  distinct from the `Company` row id.

## POST /api/admin/companies/`<id>`/decision

Used by Company Applications' Approve (green) and Reject buttons.

**Request**:
```json
{ "status": "approved" }
```

**Responses**:
- `200` — `{ "id": 1, "approval_status": "approved" }`
- `400` — `status` missing or not one of `approved`/`rejected`: `{ "error": "..." }`
- `404` — no such Company: `{ "error": "Company not found" }`

## GET /api/admin/students

Backs Registered Students.

**Query params**: `q` (optional, substring match on `name`, the account's `username`, or `contact`).

**Responses**:
- `200` —
  ```json
  [
    {
      "id": 1,
      "user_id": 3,
      "username": "john_doe",
      "name": "John Doe",
      "contact": "john@example.com",
      "is_active": true
    }
  ]
  ```

## GET /api/admin/job-positions

Backs Ongoing Drives. Always called with `status=ongoing` from the dashboard; `status` stays a query
param (not hardcoded server-side) so a completed Drive can still be looked up directly if ever needed.

**Query params**: `status` (`ongoing` | `completed`, optional — omitting it returns every Drive).

**Responses**:
- `200` —
  ```json
  [
    {
      "id": 1,
      "title": "Software Engineer",
      "description": "Entry-level backend role.",
      "company_name": "Acme Corp",
      "eligible_branches": "Computer Science",
      "min_cgpa": 7.0,
      "eligible_graduation_year": 2026,
      "salary": 800000,
      "skills_required": "Python, SQL",
      "status": "ongoing",
      "application_deadline": "2026-09-01T00:00:00"
    }
  ]
  ```
  The full field set is returned in the list response itself (not a separate detail endpoint) so the
  "View Details" modal has everything it needs from the row already in memory.

## POST /api/admin/job-positions/`<id>`/complete

Used by Ongoing Drives' "Mark as Complete" action. Not reversible from the UI.

**Responses**:
- `200` — `{ "id": 1, "status": "completed" }`
- `404` — no such Drive: `{ "error": "Job Posting not found" }`

## GET /api/admin/applications

Backs Student Applications. Read-only — no decision endpoint exists for this list.

**Responses**:
- `200` —
  ```json
  [
    {
      "id": 1,
      "student_name": "John Doe",
      "job_title": "Software Engineer",
      "company_name": "Acme Corp",
      "status": "applied",
      "application_date": "2026-08-01T10:00:00"
    }
  ]
  ```

## POST /api/admin/users/`<id>`/toggle-active

Flips `is_active` for a Company or Student account — the Blacklist/Whitelist action in both Registered
Companies and Registered Students. Refuses the Admin account itself (FR-008).

**Responses**:
- `200` — `{ "id": 1, "is_active": false }`
- `403` — target account is the Admin: `{ "error": "Cannot deactivate the Admin account" }`
- `404` — no such user: `{ "error": "User not found" }`
