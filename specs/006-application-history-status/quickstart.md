# Quickstart: Job Application History and Status Tracking

Assumes the app is already running per the project's normal dev setup (`make install`,
`make db-migrate`, `make db-seed`, `flask run`, `cd frontend && npm run dev`), seeded accounts
from `data-seeds/seed_data.py` (`admin`/`admin123`, `acme_corp`/`company123`,
`john_doe`/`student123`).

## Scenario 1: full status lifecycle → placement confirmation (US1)

1. Log in as `acme_corp`. Open an application from one of its drives (create one first if none
   exist — see Milestone 4/5 quickstarts).
2. Move its status: Shortlisted → Interview → Offer. Confirm each save succeeds and the
   dropdown reflects the new value on reload.
3. Move it to Placed, supplying a position title, salary, and joining date. Confirm the save
   succeeds.
4. Attempt to change its status again (e.g. back to Shortlisted). Expect a rejected request
   (final outcome).
5. Log in as `john_doe` (or whichever Student owns that application). Open "Download Placement
   Confirmation" — it must now succeed and show the details entered in step 3.

## Scenario 2: Student sees complete history in one place (US2)

1. As a Student with applications in multiple statuses, open the History view.
2. Confirm every application appears with status, company/job title, interview info (if any),
   remark (if any), and — for the Placed one from Scenario 1 — its placement outcome.

## Scenario 3: Admin/Company view a Student's full profile (US3)

1. As Admin, open "Registered Students," pick a Student, click "View Profile." Confirm branch,
   graduation year, CGPA, skills, contact, and resume/photo links all appear, along with that
   Student's full application list.
2. As a Company, open "Review Application" for one of that Student's applications. Confirm
   graduation year and contact now appear alongside the CGPA/branch/skills already shown.

## Scenario 4: live approval gating (US4)

1. As Admin, approve a Company, and as that Company, create an ongoing drive.
2. As a Student, confirm that Company and drive appear in Organizations/Drives.
3. As Admin, set that Company's status back to `rejected` (revoking approval).
4. As the same Student, reload Organizations/Drives — the Company and its drive must no longer
   appear. Attempt a direct `POST /api/student/drives/<id>/apply` for that drive's id — expect
   a 404.
5. Confirm any *pre-existing* application/placement for that Company (from before revocation)
   still appears in the Student's own history (Scenario 2) and in Admin/Company views —
   history is never hidden retroactively.

## Verifying the status-vocabulary migration itself

After running `flask db upgrade`, confirm no `Application` rows have `status IN ('waiting',
'selected')` left (`sqlite3 app.db "SELECT DISTINCT status FROM application;"` should show only
the six new values that are actually in use).
