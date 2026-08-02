# Company API Contract

Base path: `/api/company`. All requests/responses are JSON. Every endpoint below requires an active
session with `role == "company"` **and** `company_profile.approval_status == "approved"` (the new
`company_approved_required` decorator) — no active session is `401`, wrong role is `403`, right role
but not approved is `403` with `{"error": "Company is not yet approved"}` (per Milestone 2's contract).
Every endpoint also scopes to the caller's own Company — a Drive or Application belonging to another
Company returns `404`, not `403`, so a Company can't distinguish "not mine" from "doesn't exist."

## POST /api/company/drives

**Request**:
```json
{
  "drive_name": "Drive 3",
  "title": "Data Scientist",
  "description": "...",
  "eligibility_criteria": "B.Tech CSE/IT, CGPA >= 7.0, 2026 batch",
  "salary": 1200000,
  "location": "Bangalore",
  "application_deadline": "2026-09-01T00:00:00"
}
```

**Responses**:
- `201` — the created Drive, same shape as the list response below.
- `400` — `drive_name`, `title`, or `application_deadline` missing: `{ "error": "..." }`

## GET /api/company/drives

**Query params**: `status` (`ongoing` | `completed`, optional — omitting returns both).

**Responses**:
- `200` —
  ```json
  [
    {
      "id": 1,
      "drive_name": "Drive 3",
      "title": "Data Scientist",
      "description": "...",
      "eligibility_criteria": "...",
      "salary": 1200000,
      "location": "Bangalore",
      "status": "ongoing",
      "application_deadline": "2026-09-01T00:00:00"
    }
  ]
  ```
  Scoped to the caller's own Company only.

## POST /api/company/drives/`<id>`/complete

**Responses**:
- `200` — `{ "id": 1, "status": "completed" }`
- `404` — no such Drive, or it belongs to another Company.

## GET /api/company/drives/`<id>`/applications

Backs the "Update Applications for the Drive" screen.

**Responses**:
- `200` —
  ```json
  [
    {
      "id": 1,
      "student_name": "John Doe",
      "status": "applied",
      "application_date": "2026-08-01T10:00:00"
    }
  ]
  ```
- `404` — no such Drive, or it belongs to another Company.

## GET /api/company/applications/`<id>`

Backs the "Student Application" detail screen.

**Responses**:
- `200` —
  ```json
  {
    "id": 1,
    "student_name": "John Doe",
    "student_branch": "Computer Science",
    "student_photo_url": "/static/uploads/photos/john_doe.png",
    "student_resume_url": "/static/uploads/resumes/john_doe.pdf",
    "drive_name": "Drive 3",
    "job_title": "Data Scientist",
    "status": "applied",
    "interview_datetime": null
  }
  ```
- `404` — no such Application, or it's against a Drive belonging to another Company.

## POST /api/company/applications/`<id>`/decision

**Request**:
```json
{ "status": "shortlisted" }
```

**Responses**:
- `200` — `{ "id": 1, "status": "shortlisted" }`
- `400` — `status` missing or not one of `shortlisted`/`waiting`/`selected`/`rejected`.
- `404` — no such Application, or it's against a Drive belonging to another Company.

## POST /api/company/applications/`<id>`/interview

**Request**:
```json
{ "interview_datetime": "2026-08-15T14:00:00" }
```

**Responses**:
- `200` — `{ "id": 1, "interview_datetime": "2026-08-15T14:00:00" }`
- `400` — `interview_datetime` missing or not a valid ISO datetime.
- `404` — no such Application, or it's against a Drive belonging to another Company.
