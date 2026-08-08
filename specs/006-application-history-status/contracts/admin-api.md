# Contract: `/api/admin` changes

One new endpoint. All existing endpoints unchanged.

## `GET /admin/students/<id>` (new)

`role_required("admin")`. `404` if no Student with that id exists.

**Response** (200):
```json
{
  "id": 1,
  "user_id": 1,
  "username": "john_doe",
  "is_active": true,
  "name": "John Doe",
  "branch": {"id": 1, "code": "CSE", "name": "...", "description": "..."},
  "graduation_year": 2026,
  "cgpa": 8.5,
  "skills": [{"id": 1, "name": "Python"}],
  "contact": "...",
  "photo_url": "...",
  "resume_url": "...",
  "applications": [
    {
      "id": 1,
      "job_title": "...",
      "company_name": "...",
      "status": "interview",
      "application_date": "...",
      "interview_datetime": "... or null",
      "interview_mode": "... or null",
      "company_remark": "... or null",
      "placement": {"position_title": "...", "salary": 0, "joining_date": "..."} 
    }
  ]
}
```

`applications[].placement` is `null` unless that application's status is `placed` — same rule
as the Student-facing `GET /student/applications` change in `student-api.md`.
