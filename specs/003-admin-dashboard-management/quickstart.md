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

## US1 — Company approve/reject unlocks Registered Companies

```bash
curl -i -c /tmp/company_cookies.txt -X POST http://localhost:5000/api/auth/register/company \
  -H "Content-Type: application/json" \
  -d '{"username":"pending_co","password":"secret123","company_name":"Pending Co"}'

curl -i -b /tmp/admin_cookies.txt "http://localhost:5000/api/admin/companies?status=pending"
# expect 200, includes "pending_co"

curl -i -b /tmp/admin_cookies.txt -X POST \
  http://localhost:5000/api/admin/companies/<id>/decision \
  -H "Content-Type: application/json" -d '{"status":"approved"}'
# expect 200, {"approval_status": "approved"}

curl -i -b /tmp/admin_cookies.txt "http://localhost:5000/api/admin/companies?status=approved"
# expect 200, now includes "pending_co"
curl -i -b /tmp/admin_cookies.txt "http://localhost:5000/api/admin/companies?status=pending"
# expect 200, no longer includes "pending_co"
```

Repeat with a second Company and `{"status":"rejected"}` — confirm it never shows up under
`status=approved`, and drops out of `status=pending` too.

## US2 — Blacklist/whitelist, and Admin can't be touched

```bash
curl -i -b /tmp/admin_cookies.txt -X POST \
  http://localhost:5000/api/admin/users/<student_user_id>/toggle-active
# expect 200, {"is_active": false}   <- this is "Blacklist"

curl -i -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<that student>","password":"<their password>"}'
# expect 403 - blacklisted, per Milestone 2's existing check

curl -i -b /tmp/admin_cookies.txt -X POST \
  http://localhost:5000/api/admin/users/<student_user_id>/toggle-active
# expect 200, {"is_active": true}   <- this is "Whitelist" - login works again

curl -i -b /tmp/admin_cookies.txt -X POST \
  http://localhost:5000/api/admin/users/<admin_user_id>/toggle-active
# expect 403, "Cannot deactivate the Admin account"
```

## US3 — Search Registered Companies and Students together

```bash
curl -i -b /tmp/admin_cookies.txt "http://localhost:5000/api/admin/companies?status=approved&q=acme"
# expect 200, only companies with "acme" in name/industry

curl -i -b /tmp/admin_cookies.txt "http://localhost:5000/api/admin/students?q=doe"
# expect 200, only students matching name/username/contact

curl -i -b /tmp/admin_cookies.txt "http://localhost:5000/api/admin/students?q=nonexistent"
# expect 200, []
```

## US4 — Ongoing Drives: view details and mark complete

No Milestone-4 "create Drive" endpoint exists yet, so seed one directly:

```bash
flask shell
>>> from app.models import JobPosition, Company
>>> from app import db
>>> from datetime import datetime, timedelta
>>> co = Company.query.filter_by(company_name="Acme Corp").first()
>>> jp = JobPosition(company_id=co.id, title="Backend Intern",
...     application_deadline=datetime.utcnow() + timedelta(days=30))
>>> db.session.add(jp); db.session.commit()
>>> jp.status  # expect "ongoing" - the new default
```

```bash
curl -i -b /tmp/admin_cookies.txt "http://localhost:5000/api/admin/job-positions?status=ongoing"
# expect 200, includes "Backend Intern" with full detail fields

curl -i -b /tmp/admin_cookies.txt -X POST \
  http://localhost:5000/api/admin/job-positions/<id>/complete
# expect 200, {"status": "completed"}

curl -i -b /tmp/admin_cookies.txt "http://localhost:5000/api/admin/job-positions?status=ongoing"
# expect 200, "Backend Intern" no longer present
```

## US5 — Student Applications, read-only

```bash
curl -i -b /tmp/admin_cookies.txt http://localhost:5000/api/admin/applications
# expect 200, every application across every student and company - compare count to
# a direct table count to confirm 100% coverage (SC-008)
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

Log in as Admin and confirm, all on the one `/admin` page:
- "Welcome Admin" header with live totals.
- The one search field filters Registered Companies and Registered Students together, leaving Company
  Applications/Ongoing Drives/Student Applications untouched.
- Approving/rejecting a Company in Company Applications moves/removes it correctly.
- Blacklist/Whitelist buttons toggle color and label immediately.
- Ongoing Drives' View Details opens a modal with full Drive info; Mark as Complete removes the row.
- Student Applications' View opens a read-only modal with no action buttons inside it.
