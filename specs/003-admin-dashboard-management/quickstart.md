# Quickstart: Verifying Admin Dashboard & Management

No automated tests (see research.md). Verify with `curl` against the running Flask API, then a quick
pass in the browser against the Vue app.

## Prerequisites

- `make db-migrate && make db-seed`
- `flask run` running on :5000
- Log in as Admin and keep the cookie jar for every call below:
  ```bash
  curl -i -c /tmp/admin_cookies.txt -X POST http://localhost:5000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}'
  ```

## US1 — Dashboard totals

```bash
curl -i -b /tmp/admin_cookies.txt http://localhost:5000/api/admin/dashboard
# expect 200, {"students": N, "companies": N, "job_positions": N, "applications": N}
```

Register one more Student (Milestone 2's endpoint), reload the dashboard, and confirm `students`
incremented by 1.

## US2 — Company approve/reject

```bash
curl -i -c /tmp/company_cookies.txt -X POST http://localhost:5000/api/auth/register/company \
  -H "Content-Type: application/json" \
  -d '{"username":"pending_co","password":"secret123","company_name":"Pending Co"}'

curl -i -b /tmp/admin_cookies.txt http://localhost:5000/api/admin/companies?status=pending
# expect 200, includes "pending_co"

curl -i -b /tmp/admin_cookies.txt -X POST \
  http://localhost:5000/api/admin/companies/<id>/decision \
  -H "Content-Type: application/json" -d '{"status":"approved"}'
# expect 200, {"approval_status": "approved"}

curl -i -b /tmp/company_cookies.txt http://localhost:5000/api/auth/me
# expect 200, {"approval_status": "approved"}
```

Repeat with `{"status":"rejected"}` on a second pending Company and confirm it stays blocked
(re-check via `/api/auth/me` for that company's session).

## US3 — Job Posting approve/reject

Requires a Job Posting to exist. Until Milestone 4 adds a company-facing "create posting" endpoint,
seed one directly:

```bash
flask shell
>>> from app.models import JobPosition, Company
>>> from app import db
>>> from datetime import datetime, timedelta
>>> co = Company.query.filter_by(company_name="Pending Co").first()
>>> jp = JobPosition(company_id=co.id, title="Backend Intern",
...     application_deadline=datetime.utcnow() + timedelta(days=30))
>>> db.session.add(jp); db.session.commit()
```

```bash
curl -i -b /tmp/admin_cookies.txt http://localhost:5000/api/admin/job-positions?status=pending
# expect 200, includes "Backend Intern"

curl -i -b /tmp/admin_cookies.txt -X POST \
  http://localhost:5000/api/admin/job-positions/<id>/decision \
  -H "Content-Type: application/json" -d '{"status":"approved"}'
# expect 200, {"status": "approved"}
```

## US4 — Search

```bash
curl -i -b /tmp/admin_cookies.txt "http://localhost:5000/api/admin/companies?q=acme"
# expect 200, only companies with "acme" in name/industry

curl -i -b /tmp/admin_cookies.txt "http://localhost:5000/api/admin/students?q=doe"
# expect 200, only students matching name/username/contact

curl -i -b /tmp/admin_cookies.txt "http://localhost:5000/api/admin/students?q=nonexistent"
# expect 200, []
```

## US5 — View all Job Postings and Applications regardless of status

```bash
curl -i -b /tmp/admin_cookies.txt http://localhost:5000/api/admin/job-positions
# expect 200, every posting (pending, approved, rejected) - no status filter applied

curl -i -b /tmp/admin_cookies.txt http://localhost:5000/api/admin/applications
# expect 200, every application across every student and company
```

## US6 — Deactivate/reactivate, and Admin can't be touched

```bash
curl -i -b /tmp/admin_cookies.txt -X POST \
  http://localhost:5000/api/admin/users/<student_user_id>/toggle-active
# expect 200, {"is_active": false}

curl -i -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<that student>","password":"<their password>"}'
# expect 403 - deactivated, per Milestone 2's existing check

curl -i -b /tmp/admin_cookies.txt -X POST \
  http://localhost:5000/api/admin/users/<student_user_id>/toggle-active
# expect 200, {"is_active": true} - login works again

curl -i -b /tmp/admin_cookies.txt -X POST \
  http://localhost:5000/api/admin/users/<admin_user_id>/toggle-active
# expect 403, "Cannot deactivate the Admin account"
```

## Role check (reused from Milestone 2)

```bash
curl -i -b /tmp/company_cookies.txt http://localhost:5000/api/admin/dashboard
# expect 403 - Company can't reach any Admin endpoint
```

## Frontend smoke test

```bash
make frontend-build   # or: cd frontend && npm run dev
```

Log in as Admin and confirm:
- `/admin` shows real totals (not the Milestone 2 ping placeholder).
- Links/tabs to Companies, Students, Job Postings, and Applications each load real data from the API
  above.
- Approving/rejecting a Company or Job Posting from the UI updates its status without a page reload.
- Toggling a Student's active state from the UI reflects immediately in that row.
