# Admin API Contract

Base path: `/api/admin`. All requests/responses are JSON. Every endpoint below requires an active
session with `role == "admin"` (the existing `role_required("admin")` decorator from Milestone 2) — no
active session is `401`, an active session with the wrong role is `403`, exactly as documented in
Milestone 2's contract.

## GET /api/admin/dashboard

**Responses**:
- `200` —
  ```json
  { "students": 12, "companies": 5, "job_positions": 8, "applications": 23 }
  ```

## GET /api/admin/companies

**Query params** (both optional): `status` (`pending` | `approved` | `rejected`), `q` (substring match
on `company_name` or `industry`).

**Responses**:
- `200` —
  ```json
  [
    {
      "id": 1,
      "username": "acme_corp",
      "company_name": "Acme Corp",
      "industry": "Software",
      "approval_status": "pending",
      "is_active": true
    }
  ]
  ```

## POST /api/admin/companies/`<id>`/decision

**Request**:
```json
{ "status": "approved" }
```

**Responses**:
- `200` — `{ "id": 1, "approval_status": "approved" }`
- `400` — `status` missing or not one of `approved`/`rejected`: `{ "error": "..." }`
- `404` — no such Company: `{ "error": "Company not found" }`

## GET /api/admin/students

**Query params**: `q` (optional, substring match on `name`, the account's `username`, or `contact`).

**Responses**:
- `200` —
  ```json
  [
    {
      "id": 1,
      "username": "john_doe",
      "name": "John Doe",
      "contact": "john@example.com",
      "is_active": true
    }
  ]
  ```

## GET /api/admin/job-positions

**Query params** (both optional): `status` (`pending` | `approved` | `rejected`), `q` (substring match
on `title` or the owning Company's `company_name`).

**Responses**:
- `200` —
  ```json
  [
    {
      "id": 1,
      "title": "Software Engineer",
      "company_name": "Acme Corp",
      "status": "pending",
      "application_deadline": "2026-09-01T00:00:00"
    }
  ]
  ```

## POST /api/admin/job-positions/`<id>`/decision

**Request**:
```json
{ "status": "rejected" }
```

**Responses**:
- `200` — `{ "id": 1, "status": "rejected" }`
- `400` — `status` missing or not one of `approved`/`rejected`: `{ "error": "..." }`
- `404` — no such Job Posting: `{ "error": "Job Posting not found" }`

## GET /api/admin/applications

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

Flips `is_active` for a Company or Student account. Refuses the Admin account itself (FR-012).

**Responses**:
- `200` — `{ "id": 1, "is_active": false }`
- `403` — target account is the Admin: `{ "error": "Cannot deactivate the Admin account" }`
- `404` — no such user: `{ "error": "User not found" }`
