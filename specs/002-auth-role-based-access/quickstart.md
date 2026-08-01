# Quickstart: Verifying Authentication & Role-Based Access

No automated tests (see research.md). Verify with `curl` against the running Flask API, then a quick
pass in the browser against the Vue app.

## Prerequisites

- Milestone 1's database exists and is seeded: `make db-migrate && make db-seed`
- `flask run` running on :5000

## US1 — Student self-registers and logs in

```bash
curl -i -c /tmp/cookies.txt -X POST http://localhost:5000/api/auth/register/student \
  -H "Content-Type: application/json" \
  -d '{"username":"new_student","password":"secret123","name":"New Student"}'
# expect 201

curl -i -c /tmp/cookies.txt -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"new_student","password":"secret123"}'
# expect 200, {"role": "student", ...}

curl -i -b /tmp/cookies.txt http://localhost:5000/api/auth/me
# expect 200, same user back
```

Re-run the registration call again with the same username — expect `409` (SC covered implicitly by
FR-001's acceptance scenario 2).

## US2 — Admin: only the pre-seeded account works, no registration path exists

```bash
curl -i http://localhost:5000/api/auth/register/admin
# expect 404 - the route doesn't exist at all

curl -i -c /tmp/admin_cookies.txt -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# expect 200, {"role": "admin"}
```

## US3 — Company registers, logs in, sees pending state, gets blocked, then unblocked after approval

```bash
curl -i -c /tmp/company_cookies.txt -X POST http://localhost:5000/api/auth/register/company \
  -H "Content-Type: application/json" \
  -d '{"username":"new_co","password":"secret123","company_name":"New Co"}'
# expect 201, {"approval_status": "pending"}

curl -i -c /tmp/company_cookies.txt -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"new_co","password":"secret123"}'
# expect 200, {"approval_status": "pending"}
```

There is no company-only capability to call yet (Milestone 4 adds it) — confirm the pending state is
visible via `/api/auth/me`, and re-verify the block once Milestone 4 exists.

## US4 — Role checks and unauthenticated access

```bash
curl -i -b /tmp/cookies.txt http://localhost:5000/api/auth/logout   # log the student out
curl -i -b /tmp/cookies.txt http://localhost:5000/api/auth/me
# expect 401 - session ended
```

Once Milestone 3+ endpoints exist, repeat: log in as Student, call a Company-only or Admin-only
endpoint directly (not through the UI) → expect `403`. Log in as Company, call an Admin-only endpoint
→ expect `403`.

## Deactivated account (edge case)

```bash
flask shell
>>> from app.models import User
>>> from app import db
>>> u = User.query.filter_by(username="new_student").first()
>>> u.is_active = False
>>> db.session.commit()
```

```bash
curl -i -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"new_student","password":"secret123"}'
# expect 403, "This account has been deactivated" - even though the password is correct
```

## Frontend smoke test

```bash
cd frontend && npm install && npm run dev
```

Open the printed local URL, and confirm:
- `/register/student` and `/register/company` forms submit and redirect to `/login` on success.
- `/login` logs in and lands on the role-appropriate placeholder page (`/admin`, `/company`, or
  `/student`).
- Refreshing the browser on `/student` (or any role page) keeps you there rather than 404ing —
  proves the Flask catch-all + Jinja shell are wired correctly for client-side routes.
- Visiting a role page for a role you're not logged in as redirects to `/login`.
