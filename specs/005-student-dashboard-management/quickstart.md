# Quickstart: Verifying Student Dashboard & Job Application System

No automated tests (see research.md). Verify with `curl` against the running Flask API, then a quick
pass in the browser against the Vue app.

## Prerequisites

- `make db-migrate && make db-seed`
- `flask run` running on :5000
- Log in as the seeded Student and keep the cookie jar:
  ```bash
  curl -i -c /tmp/student_cookies.txt -X POST http://localhost:5000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"john_doe","password":"student123"}'
  ```

## US1 — Update profile (including file upload)

```bash
curl -i -b /tmp/student_cookies.txt -X POST http://localhost:5000/api/student/profile \
  -F "branch=Information Technology" -F "cgpa=9.0" \
  -F "photo=@/path/to/some/local/image.png"
# expect 200, updated fields reflected

curl -i -b /tmp/student_cookies.txt http://localhost:5000/api/student/profile
# expect 200, photo_url now points at the newly uploaded file
```

Then check Admin's existing Registered Students view (Milestone 3) shows the same updated data:

```bash
curl -i -b /tmp/admin_cookies.txt http://localhost:5000/api/admin/students
```

## US2 — Browse Organizations → Company → Drive

```bash
curl -i -b /tmp/student_cookies.txt http://localhost:5000/api/student/organizations
# expect 200, only approved Companies (e.g. Acme Corp)

curl -i -b /tmp/student_cookies.txt http://localhost:5000/api/student/organizations/1
# expect 200, includes "overview"

curl -i -b /tmp/student_cookies.txt "http://localhost:5000/api/student/drives?company_id=1"
# expect 200, only that Company's ongoing Drives

curl -i -b /tmp/student_cookies.txt http://localhost:5000/api/student/drives/1
# expect 200, full detail including company_logo_url and eligibility_criteria
```

## US3 — Apply

```bash
curl -i -b /tmp/student_cookies.txt -X POST http://localhost:5000/api/student/drives/1/apply
# expect 201 (or 409 if already applied from an earlier run)

curl -i -b /tmp/student_cookies.txt -X POST http://localhost:5000/api/student/drives/1/apply
# expect 409 - duplicate application refused

# Mark drive 1 completed via the Company API (Milestone 4), then:
curl -i -b /tmp/company_cookies.txt -X POST http://localhost:5000/api/company/drives/1/complete
curl -i -b /tmp/student_cookies.txt -X POST http://localhost:5000/api/student/drives/1/apply
# expect 409 - can't apply to a completed Drive
```

## US4 — Track status, interview, and remark

```bash
# As the Company, set a decision with a remark and an interview with a mode:
curl -i -b /tmp/company_cookies.txt -X POST \
  http://localhost:5000/api/company/applications/1/decision \
  -H "Content-Type: application/json" \
  -d '{"status":"selected","remark":"Great fit."}'

curl -i -b /tmp/company_cookies.txt -X POST \
  http://localhost:5000/api/company/applications/1/interview \
  -H "Content-Type: application/json" \
  -d '{"interview_datetime":"2026-08-15T14:00:00","mode":"in_person"}'

# As the Student, confirm all of it shows up:
curl -i -b /tmp/student_cookies.txt http://localhost:5000/api/student/applications
# expect 200, status "selected", remark "Great fit.", mode "in_person"
```

## FR-011 — Company filters/sorts its Applicants list

```bash
curl -i -b /tmp/company_cookies.txt "http://localhost:5000/api/company/drives/1/applications?status=applied"
# expect 200, only applications still in "applied" status

curl -i -b /tmp/company_cookies.txt "http://localhost:5000/api/company/drives/1/applications?sort=status"
# expect 200, every applicant, grouped by status
```

## US5 — Search

```bash
curl -i -b /tmp/student_cookies.txt "http://localhost:5000/api/student/drives?q=acme"
# expect 200, only Drives from a matching Company

curl -i -b /tmp/student_cookies.txt "http://localhost:5000/api/student/drives?q=nonexistent"
# expect 200, []
```

## US6 — Placement confirmation

```bash
curl -i -b /tmp/student_cookies.txt http://localhost:5000/api/student/placement/confirmation
# expect 200 if the seeded Placement exists for this Student, text/plain with the right details

# For a Student with no Placement:
curl -i -b /tmp/other_student_cookies.txt http://localhost:5000/api/student/placement/confirmation
# expect 404
```

## Role check (reused from Milestones 2-4)

```bash
curl -i -b /tmp/company_cookies.txt http://localhost:5000/api/student/organizations
# expect 403 - Company can't reach any Student endpoint

curl -i http://localhost:5000/api/student/organizations
# expect 401 - no session
```

## Frontend smoke test

```bash
make frontend-build   # or: cd frontend && npm run dev
```

Log in as `john_doe` and confirm, all on the one `/student` page:
- "edit profile" opens a form (including file inputs) and saves correctly.
- Organizations lists approved Companies; opening one shows its overview and Current Drives.
- Opening a Drive shows full detail with Apply/Go Back; Apply succeeds once, is blocked the second
  time.
- Applied Drives (dashboard) and the full History screen both show the Student's own Applications,
  with status/interview/remark exactly as Company set them.
- The placement confirmation download works if a Placement exists for this Student.
