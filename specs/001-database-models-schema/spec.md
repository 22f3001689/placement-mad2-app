# Feature Specification: Database Models & Schema

**Feature Branch**: `001-database-models-schema`

**Created**: 2026-08-01

**Status**: Draft

**Input**: Milestone 1 (per official Milestones doc) — "Database Models and Schema Setup (Flask)". Create the
foundational data model for the Placement Portal Application: User (role: Admin/Company/Student), Company
profile, Student profile, Job Position (a.k.a. Placement Drive), Application, and Placement, with the
relationships between them, and a pre-created Admin user. This is the schema every later milestone (auth,
dashboards, applications, jobs) is built on top of.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin exists the moment the app is set up (Priority: P1)

A fresh checkout of the project, after running the setup steps, already has exactly one Admin account —
nobody registers as Admin through the app.

**Why this priority**: Every other role's approval workflow (Company approval, drive approval) depends on
an Admin existing. Without this, no other milestone can be demoed.

**Independent Test**: Wipe the database, run the setup/seed step, and confirm exactly one Admin user exists
that can be identified by role, with no code path in the app that can create a second one.

**Acceptance Scenarios**:

1. **Given** an empty database, **When** the seed step runs, **Then** exactly one user with role `admin`
   exists.
2. **Given** the seed step has already run once, **When** it is run again, **Then** it does not create a
   duplicate Admin (it is safe to re-run).

---

### User Story 2 - Every person in the system has exactly one role and one profile (Priority: P1)

A Student and a Company can both exist in the system as distinct account types, each with the profile
details relevant to their role, without the two ever being confused with each other or with Admin.

**Why this priority**: Role-based access (Milestone 2) and every dashboard (Milestones 3–5) read from these
profiles — if the shape is wrong here, it has to be redone everywhere downstream.

**Independent Test**: Create one User row per role directly against the schema (Admin, Company, Student),
attach the role-specific profile row to the Company and Student users, and confirm each can be looked up by
its role and its profile fields.

**Acceptance Scenarios**:

1. **Given** a new user registers as a Student, **When** their record is saved, **Then** a linked Student
   profile (education, skills, resume, etc.) exists for that user and no Company profile does.
2. **Given** a new user registers as a Company, **When** their record is saved, **Then** a linked Company
   profile (name, industry, location, HR contact, approval status, etc.) exists for that user and no
   Student profile does.

---

### User Story 3 - A Company's job posting, and who applied to it, can be recorded and traced (Priority: P2)

A Company can have one or more Job Positions (Placement Drives) recorded against it, and Students can have
Application records tying them to a specific Job Position, with a status that can change over time.

**Why this priority**: This is the core relationship the entire application exists to manage, but it only
becomes usable once Milestone 1's user/company/student stories above are in place, and it is exercised for
real starting in Milestones 3–5 — the schema needs to exist now so those milestones aren't blocked.

**Independent Test**: Create a Company, give it a Job Position, create a Student, and create an Application
linking that Student to that Job Position; confirm the Application can be traced back to both the Student
and the Job Position, and that the Job Position can list all Applications against it.

**Acceptance Scenarios**:

1. **Given** a Company with an approved profile, **When** a Job Position is recorded for that company,
   **Then** it stores the eligibility criteria (branch, CGPA, year), deadline, and status (Pending /
   Approved / Closed).
2. **Given** a Job Position, **When** a Student applies, **Then** an Application record is created linking
   Student and Job Position, with its own status (Applied / Shortlisted / Interview / Selected / Rejected)
   and application date, and it appears when listing "applications for this Job Position" and "applications
   by this Student".

---

### User Story 4 - A completed placement is recorded permanently (Priority: P3)

When a Student is finally selected and placed, that outcome is stored as its own durable record — separate
from the day-to-day Application status — so it forms the Student's placement history even if the
originating Job Position or Application is later closed.

**Why this priority**: Needed for placement history and reporting features (Milestones 5, 6), but nothing
else in Milestone 1 depends on it, so it can be the last piece added.

**Independent Test**: Take a Student with a Selected Application, create a Placement record from it, and
confirm it independently records company, position, salary, and joining date, and remains queryable after
the Job Position is closed.

**Acceptance Scenarios**:

1. **Given** an Application with status Selected, **When** a Placement record is created for it, **Then**
   it stores Student, Company, Position, Salary, and Joining Date.
2. **Given** a Job Position is later closed, **When** the Student's placement history is viewed, **Then**
   their Placement record is still present and complete.

---

### Edge Cases

- What happens if a seed script is run twice? It must not create a second Admin or duplicate seed data.
- What happens if a Student tries to apply to the same Job Position twice? The schema must make a duplicate
  Application (same student, same job position) impossible to represent as two separate rows.
- What happens to a Student's Applications/Placements if their User account is later deactivated? History
  must remain intact and queryable — deactivation is a flag, not a delete.
- What happens if a Job Position's Company is deactivated? Existing Applications and Placements against
  that Job Position must remain queryable (no cascading delete of history).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST represent every account (Admin, Company, Student) as a single row in one unified
  User concept, distinguished by a role field, with no separate login mechanism per role.
- **FR-002**: System MUST support exactly one Admin account; nothing in the schema or seed process may
  produce a second one.
- **FR-003**: System MUST attach a Company profile (company name, industry, location, HR contact, website,
  approval status) to every user with the Company role, and MUST NOT allow a Company profile to exist
  without a corresponding Company-role user.
- **FR-004**: System MUST attach a Student profile (name, education details, skills, resume reference,
  contact info) to every user with the Student role, and MUST NOT allow a Student profile to exist without
  a corresponding Student-role user.
- **FR-005**: System MUST record Job Positions (Placement Drives) against exactly one Company, storing at
  minimum: title, description, eligibility criteria (branch, minimum CGPA, graduation year), salary,
  required skills, application deadline, and status (Pending / Approved / Closed).
- **FR-006**: System MUST record Applications linking exactly one Student to exactly one Job Position,
  storing application date and a status that can move through Applied / Shortlisted / Interview / Selected
  / Rejected.
- **FR-007**: System MUST prevent a Student from having more than one Application against the same Job
  Position at the schema level (not left to application-code checks alone).
- **FR-008**: System MUST record Placements as their own entity (Student, Company, Position, Salary,
  Joining Date), independent of whether the originating Job Position or Application still exists in an
  active state.
- **FR-009**: System MUST support marking a Company or Student as blacklisted/deactivated without deleting
  their historical data (profile, applications, placements all remain intact and queryable).
- **FR-010**: System MUST allow a Company to have many Job Positions, and a Job Position to have many
  Applications (1:n relationships); a Student may have many Applications and at most one Placement per
  Application.
- **FR-011**: The schema MUST be created entirely through code (models/migrations) — no manually-authored
  database file.

### Key Entities

- **User**: Any account in the system. Holds login identity and a role (Admin / Company / Student) plus an
  active/blacklisted flag. Exactly one Admin ever exists.
- **Company**: Profile data for a Company-role user — company name, industry, location, HR contact,
  website, and approval status (Pending / Approved / Rejected). One-to-one with a Company-role User.
- **Student**: Profile data for a Student-role user — name, education/branch/year, CGPA, skills, resume
  reference, contact info. One-to-one with a Student-role User.
- **Job Position (Placement Drive)**: A recruitment opening posted by a Company — title, description,
  eligibility criteria, salary, deadline, status. Many-to-one with Company; one-to-many with Application.
- **Application**: A Student's application to one Job Position — application date, status. Many-to-one
  with both Student and Job Position; unique per (Student, Job Position) pair.
- **Placement**: A finalized placement outcome for a Student — company, position, salary, joining date.
  Linked to the Student (and typically originates from a Selected Application) but persists independently.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After the one-time setup/seed step, the system has exactly one Admin account, verifiable by
  a direct query, with zero manual database edits involved.
- **SC-002**: Every Company and Student account created afterward has its role-specific profile fully
  populated and retrievable in a single lookup by that account.
- **SC-003**: A Student can never end up with two Application rows for the same Job Position — attempting
  to create a second one fails outright rather than silently producing a duplicate.
- **SC-004**: A Student's placement and application history remains fully readable even after the related
  Company is deactivated or the Job Position is closed.
- **SC-005**: The full schema can be rebuilt from a clean database using only code (model definitions and/or
  migrations plus the seed script) — no step in the process requires a database GUI tool.

## Assumptions

- "Job Position" (Milestones doc wording) and "Placement Drive" (Project Statement wording) refer to the
  same entity; this spec uses "Job Position" as the primary name and treats "Placement Drive" as a synonym.
- A Student profile is created at Student self-registration time (Milestone 2 builds the registration flow
  itself); this milestone only needs the schema and relationship to exist and be exercisable directly.
- One Application can produce at most one Placement; a Student can hold multiple Placements over time only
  if they have multiple Selected Applications (e.g., across different years) — the schema does not need to
  prevent multiple Placements per Student, only per Application.
- Resume storage is a file reference (path/URL) on the Student profile; the file upload mechanism itself is
  out of scope for this milestone (belongs to the Student dashboard milestone).
- No auth/session logic, no API endpoints, and no Vue UI are in scope here — purely the data model and its
  enforced constraints, plus the Admin seed script.
