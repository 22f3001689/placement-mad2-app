# Contract: `/api/company` changes

All existing endpoints keep their existing shape except the two below. Both remain under
`company_approved_required`.

## `POST /company/applications/<id>/decision` (changed)

**Request body**:
```json
{
  "status": "shortlisted | interview | offer | rejected | placed",
  "remark": "optional string, unchanged from today",
  "position_title": "required only when status=placed",
  "salary": "optional integer, only meaningful when status=placed",
  "joining_date": "required only when status=placed, ISO date (YYYY-MM-DD)"
}
```

**Behavior changes**:
- `status` must be one of the five values above (was: `shortlisted/waiting/selected/rejected`).
  `400` with an explicit error message otherwise.
- If the application's *current* status is already `placed` or `rejected`, respond `409`
  ("This application's outcome is final") and make no change.
- If `status="placed"`: `position_title` and `joining_date` are required (`400` if missing);
  a `Placement` row is created in the same request (`student_id`/`company_id` from the
  application, `application_id` = this application's id, `position_title`/`salary`/`joining_date`
  from the request body).

**Response** (200): unchanged shape, `{"id", "status", ["remark"]}` — plus, when a Placement
was created, the created placement is not echoed back here (the Student's own
`/student/applications` and `/student/placement/confirmation` already surface it).

## `GET /company/applications/<id>` (changed payload only)

Adds two fields to the existing response: `student_graduation_year`, `student_contact`.
Everything else (`student_name`, `student_branch`, `student_cgpa`, `student_skills`,
`student_photo_url`, `student_resume_url`, `drive_name`, `job_title`, `status`,
`interview_datetime`, `interview_mode`, `company_remark`) is unchanged.
