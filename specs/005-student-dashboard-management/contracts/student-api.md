# Student API Contract

Base path: `/api/student`. Every endpoint requires an active session with `role == "student"` (the
existing `role_required("student")` decorator) — no active session is `401`, wrong role is `403`.
Every Application/Drive lookup that's specific to "my own" data is scoped to the caller — another
Student's Application returns `404`, matching Milestone 4's own cross-Company isolation pattern.

## GET /api/student/profile

**Responses**:
- `200` —
  ```json
  {
    "name": "John Doe",
    "branch": "Computer Science",
    "graduation_year": 2026,
    "cgpa": 8.5,
    "skills": "Python, Flask, SQL",
    "contact": "john.doe@example.com",
    "photo_url": "/static/uploads/photos/3_john.png",
    "resume_url": "/static/uploads/resumes/3_john.pdf"
  }
  ```

## POST /api/student/profile

**Request**: `multipart/form-data` — text fields `name`, `branch`, `graduation_year`, `cgpa`,
`skills`, `contact` (all optional, only provided fields are updated), plus optional file fields
`photo`, `resume`.

**Responses**:
- `200` — same shape as `GET /api/student/profile`, reflecting the update.
- `400` — `graduation_year`/`cgpa` not a valid number: `{ "error": "..." }`

## GET /api/student/organizations

**Query params**: `q` (optional, substring match on `company_name`).

**Responses**:
- `200` —
  ```json
  [
    { "id": 1, "company_name": "Acme Corp", "industry": "Software", "logo_url": "/static/uploads/logos/acme_corp.png" }
  ]
  ```
  Only `approval_status == "approved"` Companies ever appear.

## GET /api/student/organizations/`<id>`

**Responses**:
- `200` —
  ```json
  {
    "id": 1,
    "company_name": "Acme Corp",
    "overview": "Through the application of innovation...",
    "logo_url": "/static/uploads/logos/acme_corp.png",
    "industry": "Software",
    "location": "Bangalore"
  }
  ```
- `404` — no such Company, or it isn't `approved`.

## GET /api/student/drives

Backs both a Company's "Current Drives" (`company_id` param) and Search (`q` param). Always
restricted to `status == "ongoing"` (research.md) — not a caller-supplied filter.

**Query params** (both optional): `company_id`, `q` (substring match on `company_name`, `title`/
`drive_name`, or `skills_required`).

**Responses**:
- `200` —
  ```json
  [
    { "id": 1, "drive_name": "Drive 1", "title": "Software Engineer", "company_name": "Acme Corp" }
  ]
  ```

## GET /api/student/drives/`<id>`

No status restriction (research.md) — viewable whether `ongoing` or `completed`.

**Responses**:
- `200` —
  ```json
  {
    "id": 1,
    "drive_name": "Drive 1",
    "title": "Senior Software Developer",
    "description": "an experienced developer who leads projects...",
    "salary": 600000,
    "location": "Chennai",
    "company_name": "Acme Corp",
    "company_logo_url": "/static/uploads/logos/acme_corp.png",
    "status": "ongoing",
    "already_applied": false
  }
  ```
  `already_applied` tells the frontend whether to show Apply or not, without a second request.
- `404` — no such Drive.

## POST /api/student/drives/`<id>`/apply

**Responses**:
- `201` — `{ "id": 1, "status": "applied" }`
- `404` — no such Drive.
- `409` — the Drive is `completed`, or the Student already applied to it:
  `{ "error": "..." }`

## GET /api/student/applications

Backs both the dashboard's "Applied Drives" and the full "Student Application History" screen —
same data, the frontend decides how much of it to show where.

**Responses**:
- `200` —
  ```json
  [
    {
      "id": 1,
      "job_position_id": 1,
      "drive_name": "Drive 1",
      "job_title": "Software Engineer",
      "company_name": "Acme Corp",
      "status": "selected",
      "interview_datetime": "2026-08-15T14:00:00",
      "interview_mode": "in_person",
      "company_remark": null,
      "application_date": "2026-08-02T10:00:00"
    }
  ]
  ```
  `job_position_id` lets the frontend link straight back to `GET /api/student/drives/<id>` for the
  dashboard's "view details" action, without a separate lookup.

## GET /api/student/placement/confirmation

**Responses**:
- `200` — `text/plain`, `Content-Disposition: attachment`, containing position/company/salary/
  joining date, if a `Placement` row exists for the Student.
- `404` — no `Placement` record exists: `{ "error": "No placement on file" }`

---

## Extended: Company API (Milestone 4)

Two existing endpoints gain one optional field each. Everything else about them is unchanged from
`specs/004-company-dashboard-management/contracts/company-api.md`.

### POST /api/company/applications/`<id>`/decision

**Request**:
```json
{ "status": "selected", "remark": "Strong technical round, great culture fit." }
```
`remark` is optional; omitting it leaves `company_remark` unchanged.

**Responses**: unchanged shape, now also echoing `remark` if provided —
`{ "id": 1, "status": "selected", "remark": "..." }`

### POST /api/company/applications/`<id>`/interview

**Request**:
```json
{ "interview_datetime": "2026-08-15T14:00:00", "mode": "in_person" }
```
`mode` is optional (`"in_person"` or `"virtual"`); omitting it leaves `interview_mode` unchanged.

**Responses**: unchanged shape, now also echoing `mode` if provided —
`{ "id": 1, "interview_datetime": "...", "mode": "in_person" }`
