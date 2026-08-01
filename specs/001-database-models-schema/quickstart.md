# Quickstart: Verifying the Database Models & Schema

No automated tests (see research.md). Verify by building the schema, seeding it, and poking at it via
`flask shell`.

## Prerequisites

- Python 3.11, virtualenv created via `make venv` / `make install`
- `.env` (or shell env) with `FLASK_APP=app` — same as `../hms-app-main`

## Build the schema

```bash
make db-init      # flask db init  (first time only)
make db-migrate    # flask db upgrade
```

Expected: `app.db` is created; no manual SQL, no DB Browser step.

## Seed and check the Admin invariant

```bash
make db-seed        # runs data-seeds/seed_data.py
flask shell
>>> from app.models import User
>>> User.query.filter_by(role="admin").count()
1
```

Expected: exactly `1`. Re-run `make db-seed` and check again — still `1` (SC-001).

## Check role-specific profiles round-trip

```bash
flask shell
>>> from app.models import User, Company, Student
>>> u = User.query.filter_by(role="student").first()
>>> u.student_profile.name, u.student_profile.branch
('...', '...')
>>> c = User.query.filter_by(role="company").first()
>>> c.company_profile.company_name, c.company_profile.approval_status
('...', 'approved')
```

Expected: each lookup returns populated fields in a single hop from `User` (SC-002).

## Check the duplicate-application guard

```bash
flask shell
>>> from app import db
>>> from app.models import Application, Student, JobPosition
>>> s = Student.query.first()
>>> jp = JobPosition.query.first()
>>> db.session.add(Application(student_id=s.id, job_position_id=jp.id))
>>> db.session.commit()
>>> db.session.add(Application(student_id=s.id, job_position_id=jp.id))  # same pair again
>>> db.session.commit()
```

Expected: the second `commit()` raises an `IntegrityError` from the unique constraint (SC-003).

## Check history survives deactivation/closure

```bash
flask shell
>>> from app.models import Company, JobPosition, Placement
>>> c = Company.query.first()
>>> c.user.is_active = False
>>> jp = c.job_positions[0]
>>> jp.status = "closed"
>>> db.session.commit()
>>> Placement.query.filter_by(company_id=c.id).all()   # still returns rows, unaffected
```

Expected: Placement rows tied to that company/job position are still present and fully readable (SC-004).
