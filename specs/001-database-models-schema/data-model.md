# Phase 1 Data Model: Database Models & Schema

All models live in `app/models.py`, following the `../hms-app-main` layout and naming conventions.

## User

The single login/identity table. `role` is the only thing that distinguishes an Admin, a Company, or a
Student account.

| Field | Type | Notes |
|---|---|---|
| id | Integer, PK | |
| username | String(80), unique, not null | login identifier |
| password_hash | String(128), not null | set via `set_password()` / checked via `check_password()` |
| role | String(20), not null | `admin` \| `company` \| `student` |
| is_active | Boolean, default True | flips to False on blacklist/deactivate (FR-009) |
| created_at | DateTime, default now | |

Relationships: `company_profile` (1:1 → Company, if role=company), `student_profile` (1:1 → Student, if
role=student). Both are optional at the DB level (nullable FK on the child side) — enforcing "exactly one
profile matching the role" is an application-level invariant checked wherever a User is created, not a DB
constraint (SQLite has no partial/conditional FKs worth the complexity here).

**Invariant (app-enforced, not DB-enforced)**: exactly one `role = 'admin'` row ever exists — enforced by
never exposing an admin-creation code path and only ever seeding it once (FR-002).

## Company

Profile for a Company-role User. One row per Company-role User.

| Field | Type | Notes |
|---|---|---|
| id | Integer, PK | |
| user_id | Integer, FK → User.id, unique, not null | 1:1 |
| company_name | String(150), not null | |
| industry | String(100), nullable | |
| location | String(150), nullable | |
| hr_contact | String(100), nullable | |
| website | String(255), nullable | |
| approval_status | String(20), not null, default `pending` | `pending` \| `approved` \| `rejected` |
| created_at | DateTime, default now | |

Relationships: `job_positions` (1:n → JobPosition, cascade delete-orphan — a Company's postings go with
it, but see note on Application/Placement below, which do NOT cascade).

## Student

Profile for a Student-role User. One row per Student-role User.

| Field | Type | Notes |
|---|---|---|
| id | Integer, PK | |
| user_id | Integer, FK → User.id, unique, not null | 1:1 |
| name | String(100), not null | |
| branch | String(100), nullable | |
| graduation_year | Integer, nullable | |
| cgpa | Float, nullable | |
| skills | Text, nullable | free-text/comma-separated for now — structured skill tags are a later-milestone concern, not this one |
| resume_path | String(255), nullable | file reference; upload mechanism is out of scope (FR note, Assumptions) |
| contact | String(100), nullable | |
| created_at | DateTime, default now | |

Relationships: `applications` (1:n → Application, cascade delete-orphan — deleting a Student account
record removes their applications; in practice Students are deactivated, not deleted, per FR-009),
`placements` (1:n → Placement, cascade delete-orphan, same caveat).

## JobPosition (Placement Drive)

A recruitment opening posted by a Company.

| Field | Type | Notes |
|---|---|---|
| id | Integer, PK | |
| company_id | Integer, FK → Company.id, not null | |
| title | String(150), not null | |
| description | Text, nullable | |
| eligible_branches | String(255), nullable | comma-separated branch list; empty/null = open to all |
| min_cgpa | Float, nullable | |
| eligible_graduation_year | Integer, nullable | |
| salary | Integer, nullable | annual CTC, plain integer is enough for this milestone |
| skills_required | Text, nullable | |
| application_deadline | DateTime, not null | |
| status | String(20), not null, default `pending` | `pending` \| `approved` \| `closed` |
| created_at | DateTime, default now | |

Relationships: `applications` (1:n → Application). **No cascade delete** from JobPosition to Application —
closing/removing a posting must not erase Application/Placement history (spec edge case). Deleting a
JobPosition row outright is not a supported operation in this milestone; "closed" is a status, not a
deletion.

## Application

One Student's application to one JobPosition.

| Field | Type | Notes |
|---|---|---|
| id | Integer, PK | |
| student_id | Integer, FK → Student.id, not null | |
| job_position_id | Integer, FK → JobPosition.id, not null | |
| application_date | DateTime, default now | |
| status | String(20), not null, default `applied` | `applied` \| `shortlisted` \| `interview` \| `selected` \| `rejected` |

**Constraint**: `UniqueConstraint(student_id, job_position_id)` — enforces FR-007 at the DB level.

Relationships: `student` (→ Student), `job_position` (→ JobPosition), `placement` (1:1 → Placement,
nullable — only present once status reaches `selected` and a Placement is created).

## Placement

The durable, final outcome for a Student — independent of the Application/JobPosition lifecycle.

| Field | Type | Notes |
|---|---|---|
| id | Integer, PK | |
| student_id | Integer, FK → Student.id, not null | |
| company_id | Integer, FK → Company.id, not null | denormalized alongside application_id so history reads don't need to join through a possibly-closed JobPosition |
| application_id | Integer, FK → Application.id, unique, nullable | link back to the originating application, if it still exists |
| position_title | String(150), not null | copied from JobPosition.title at creation time — a snapshot, so it survives the JobPosition changing later |
| salary | Integer, nullable | |
| joining_date | Date, nullable | |
| created_at | DateTime, default now | |

Relationships: `student` (→ Student). No cascade from Company or Application — a Placement is a snapshot,
not a live join, which is exactly what satisfies the "history survives closure/deactivation" requirement
(FR-008, edge cases).

## Relationship Summary

```text
User (1) ── (1) Company ── (1) ── (n) JobPosition ── (1) ── (n) Application ── (n) ── (1) Student ── (1) ── (1) User
                                                         │
                                                         └── (1) ── (0/1) Placement ── (n) ── (1) Student
                                                                          │
                                                                          └── (n) ── (1) Company (denormalized)
```

## Admin Seeding

`data-seeds/seed_data.py` (adapted from `../hms-app-main`'s script of the same name): creates the one
`User(role='admin')` plus a handful of sample Companies/Students/JobPositions for local demo purposes,
following the same `db.drop_all(); db.create_all(); ...` idempotent-reseed pattern already proven there.
