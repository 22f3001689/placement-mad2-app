# Quickstart: Verifying Company Dashboard & Job/Application Management

No automated tests (see research.md). Verify with `curl` against the running Flask API, then a quick
pass in the browser against the Vue app.

## Prerequisites

- `make db-migrate && make db-seed`
- `flask run` running on :5000
- Log in as the seeded Company (already approved) and keep the cookie jar:
  ```bash
  curl -i -c /tmp/company_cookies.txt -X POST http://localhost:5000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"acme_corp","password":"company123"}'
  ```

## US1 — Create a Drive

```bash
curl -i -b /tmp/company_cookies.txt -X POST http://localhost:5000/api/company/drives \
  -H "Content-Type: application/json" \
  -d '{"drive_name":"Drive 2","title":"Backend Intern","eligibility_criteria":"CS/IT, 2026 batch",
       "application_deadline":"2026-09-01T00:00:00"}'
# expect 201, status "ongoing"

curl -i -b /tmp/company_cookies.txt "http://localhost:5000/api/company/drives?status=ongoing"
# expect 200, includes "Drive 2"
```

Try the same with a pending/unapproved Company's session (register one fresh, log in, don't approve
it) and confirm `403`, `{"error": "Company is not yet approved"}`.

## US2 — Upcoming/Closed Drives, mark complete

```bash
curl -i -b /tmp/company_cookies.txt "http://localhost:5000/api/company/drives?status=ongoing"
# expect 200, only this company's ongoing drives

curl -i -b /tmp/company_cookies.txt -X POST http://localhost:5000/api/company/drives/<id>/complete
# expect 200, {"status": "completed"}

curl -i -b /tmp/company_cookies.txt "http://localhost:5000/api/company/drives?status=completed"
# expect 200, the drive now appears here instead
```

## US3 — Review a Drive's Applicants

```bash
curl -i -b /tmp/company_cookies.txt http://localhost:5000/api/company/drives/<id>/applications
# expect 200, every Application against that Drive
```

Attempt the same call against a Drive ID belonging to a different Company (seed a second
Company+Drive to test) and confirm `404`.

## US4 — Review one Application and set its status

```bash
curl -i -b /tmp/company_cookies.txt http://localhost:5000/api/company/applications/<id>
# expect 200, includes student_photo_url/student_resume_url matching what Admin already sees

curl -i -b /tmp/company_cookies.txt -X POST \
  http://localhost:5000/api/company/applications/<id>/decision \
  -H "Content-Type: application/json" -d '{"status":"shortlisted"}'
# expect 200

curl -i -b /tmp/company_cookies.txt http://localhost:5000/api/company/applications/<id>
# expect 200, status now "shortlisted"
```

Repeat with `"waiting"`, `"selected"`, and `"rejected"` — each should stick.

## US5 — Schedule an interview

```bash
curl -i -b /tmp/company_cookies.txt -X POST \
  http://localhost:5000/api/company/applications/<id>/interview \
  -H "Content-Type: application/json" -d '{"interview_datetime":"2026-08-15T14:00:00"}'
# expect 200

curl -i -b /tmp/company_cookies.txt http://localhost:5000/api/company/applications/<id>
# expect 200, interview_datetime now set
```

## Role/approval check (reused from Milestones 2-3)

```bash
curl -i -b /tmp/student_cookies.txt http://localhost:5000/api/company/drives
# expect 403 - Student can't reach any Company endpoint

curl -i http://localhost:5000/api/company/drives
# expect 401 - no session
```

## Frontend smoke test

```bash
make frontend-build   # or: cd frontend && npm run dev
```

Log in as `acme_corp` and confirm, all on the one `/company` page:
- "Create Drive" opens a modal form; submitting adds a row to Upcoming Drives.
- "view details" on an Upcoming Drive and "update" on a Closed Drive both open the same
  Applications-list modal.
- "review application" swaps to the Application-detail modal (photo, resume link, status dropdown,
  interview date/time field); "Back" returns to the Applications list.
- Every change (status, interview date/time) persists across a reload.
