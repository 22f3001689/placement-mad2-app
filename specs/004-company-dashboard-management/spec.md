# Feature Specification: Company Dashboard & Job/Application Management

**Feature Branch**: `004-company-dashboard-management`

**Created**: 2026-08-01

**Status**: Draft

**Input**: Milestone 4 (per official Milestones doc) — "Company Dashboard and Job/Application
Management (Flask+Vue)". Companies create and manage Drives, view and decide on Applications
(shortlist/waiting/select/reject), and schedule interviews with shortlisted candidates. Backed by a
provided wireframe (Company Dashboard → Create Drive form; Upcoming/Closed Drives → Update
Applications for a Drive → Student Application detail with a status dropdown).

Only an Admin-approved Company (Milestone 3's approval gate) can use any capability in this milestone —
a pending or rejected Company can still log in (Milestone 2) but every action here is blocked.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An approved Company creates a Drive (Priority: P1)

A Company fills in the Create Drive form — Drive Name, Job Title, Job Description, Eligibility
Criteria, Application Deadline — and it appears immediately in their own Upcoming Drives list, open for
Applications.

**Why this priority**: Nothing else in this milestone (or Milestone 5's "apply for jobs") has anything
to act on until a Drive exists — this is the foundational capability.

**Independent Test**: As an approved Company, submit the Create Drive form and confirm the new Drive
appears in Upcoming Drives with the fields exactly as entered.

**Acceptance Scenarios**:

1. **Given** an approved Company, **When** it submits the Create Drive form with all required fields,
   **Then** a new Drive is created, open (`ongoing`), and appears in that Company's own Upcoming Drives.
2. **Given** a required field is missing (Drive Name, Job Title, or Application Deadline), **When** the
   form is submitted, **Then** it's rejected with a clear error and no Drive is created.
3. **Given** a Company that is pending or rejected (not yet approved), **When** it attempts to create a
   Drive, **Then** the attempt is refused — this is a company-only capability gated on approval
   (Milestone 2's FR-009).

---

### User Story 2 - Company sees its own Upcoming and Closed Drives, and closes one (Priority: P1)

The Company's dashboard lists its own Drives split into Upcoming (`ongoing`) and Closed (`completed`),
each with a serial number and name; from Upcoming, it can mark a Drive complete, moving it to Closed.

**Why this priority**: This is the Company's home screen — without it there's no way to reach any other
capability in this milestone, and it directly reuses Milestone 3's existing ongoing/completed lifecycle.

**Independent Test**: As an approved Company with at least one Drive, view the dashboard and confirm it
appears under Upcoming; mark it complete and confirm it moves to Closed.

**Acceptance Scenarios**:

1. **Given** a Company with Drives in both states, **When** it views its dashboard, **Then** Upcoming
   Drives shows only its own `ongoing` Drives and Closed Drives shows only its own `completed` ones —
   never another Company's.
2. **Given** an ongoing Drive, **When** the Company marks it complete, **Then** it moves from Upcoming
   to Closed immediately, the same `status` transition Milestone 3's Admin action already performs.

---

### User Story 3 - Company reviews the list of Applicants for a Drive (Priority: P1)

From either an Upcoming Drive's "view details" or a Closed Drive's "update," the Company sees every
Student who applied to that Drive, with a "review application" action per row.

**Why this priority**: This is the entry point to the actual hiring decision (User Story 4) — without
a list of applicants, there's nothing to review.

**Independent Test**: With a Drive that has Applications from multiple Students, open its Applications
list and confirm every applicant appears, none from a different Drive.

**Acceptance Scenarios**:

1. **Given** a Drive with several Applications, **When** the Company opens its Applications list,
   **Then** every Student who applied to that specific Drive appears, and no one else's.
2. **Given** a Closed Drive, **When** the Company opens it via "update," **Then** the same Applications
   list is shown — closing a Drive to new Applications doesn't block reviewing/deciding on existing ones.

---

### User Story 4 - Company reviews one Application and sets its status (Priority: P1)

Opening "review application" shows the Student's name, department (branch), the Drive and Job Title,
their photo, a "view resume" action, and a status control — Shortlisted / Waiting / Selected / Rejected
— that the Company sets for that Application.

**Why this priority**: This is the actual hiring decision this milestone exists to support — the rest
of the milestone is scaffolding to reach this screen.

**Independent Test**: Open an Application still in its default state, set it to each status in turn,
and confirm the change is saved and visible the next time that Application is opened.

**Acceptance Scenarios**:

1. **Given** an Application in its default (`applied`) state, **When** the Company sets its status to
   Shortlisted, Waiting, Selected, or Rejected, **Then** that status is saved and shown correctly the
   next time anyone views that Application.
2. **Given** an Application belonging to a different Company's Drive, **When** this Company attempts
   to view or change its status directly, **Then** the attempt is refused.
3. **Given** a Student's photo and resume exist on file (per Milestone 3's `photo_path`/`resume_path`),
   **When** the Company opens that Student's Application, **Then** the photo renders and "view resume"
   downloads the same file Admin already sees for that Student.

---

### User Story 5 - Company schedules an interview for a shortlisted candidate (Priority: P2)

From the same Application review screen, the Company can set a date/time for that candidate's
interview.

**Why this priority**: Directly named in the Milestones doc ("Schedule interviews with shortlisted
candidates") and needed before Milestone 7 can build interview reminders on top of it — but it's a
smaller, more optional addition than the core review-and-decide flow above, so it's P2.

**Independent Test**: Set an interview date/time on an Application and confirm it's saved and shown the
next time that Application is opened.

**Acceptance Scenarios**:

1. **Given** any Application, **When** the Company sets an interview date/time on it, **Then** it's
   saved and shown correctly the next time that Application is opened.
2. **Given** an Application with no interview date/time set, **When** the Company opens it, **Then**
   the field is simply empty — scheduling one is optional, not required before setting a status.

---

### Edge Cases

- What happens if a Company tries to create a Drive while pending or rejected? Refused (User Story 1,
  Scenario 3) — the same approval gate Milestone 2/3 already established for every company-only
  capability.
- What happens if a Company tries to review or decide on an Application for a Drive that isn't its own?
  Refused (User Story 4, Scenario 2) — Drives and their Applications belong to exactly one Company.
- What happens if Admin deactivates (blacklists) a Company mid-review? Per Milestone 3's existing
  behavior, its existing Drives/Applications are untouched; the Company simply can't log in to keep
  reviewing until reactivated.
- What happens to a Drive's Applications if Admin (Milestone 3) marks the Drive complete instead of the
  Company? Same effect either way — `status` is the same column, whichever side sets it.
- What happens if the Company sets a status on an Application, then changes it again later? Allowed —
  status is not a one-way transition in this milestone; the Company can revise a decision.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let an approved Company create a Drive with a Drive Name, Job Title, Job
  Description, Eligibility Criteria, and Application Deadline, defaulting to `ongoing`.
- **FR-002**: System MUST refuse Drive creation for a Company that isn't Admin-approved.
- **FR-003**: System MUST let a Company list only its own Drives, split by status into Upcoming
  (`ongoing`) and Closed (`completed`).
- **FR-004**: System MUST let a Company mark its own `ongoing` Drive as `completed`.
- **FR-005**: System MUST let a Company list every Application against one of its own Drives, and MUST
  refuse this for a Drive it doesn't own.
- **FR-006**: System MUST let a Company view one Application's full detail: Student name, branch,
  Drive, Job Title, photo, and resume link — and MUST refuse this for an Application against a Drive it
  doesn't own.
- **FR-007**: System MUST let a Company set an Application's status to one of Shortlisted, Waiting,
  Selected, or Rejected, changeable again later.
- **FR-008**: System MUST let a Company set (and later change) an interview date/time on an
  Application; this is optional, independent of the Application's status.
- **FR-009**: System MUST refuse every capability in this milestone to any caller that isn't logged in
  as the owning Company, per the role check already established in Milestone 2.

### Key Entities

- **`JobPosition` ("Drive") gains `drive_name`**: a new, separate field from the existing `title`
  ("Job Title") — the wireframe's Create Drive form asks for both as distinct inputs (e.g. Drive Name
  "Drive 3", Job Title "Data Scientist"). Both are required.
- **`JobPosition` gains `eligibility_criteria`** (freeform text): the wireframe's Create Drive form has
  one single Eligibility Criteria text box, not the three separate structured fields
  (`eligible_branches`, `min_cgpa`, `eligible_graduation_year`) Milestone 1 speculatively added before
  any real UI existed for them.
- **Removal**: `eligible_branches`, `min_cgpa`, `eligible_graduation_year` are dropped from
  `JobPosition`. Nothing in the codebase has ever read them for actual eligibility filtering, and
  Milestone 5's own spec (student search/apply) doesn't ask for structured filtering either — keeping
  three unused, never-wired-up columns is exactly the speculative complexity the constitution's
  Karpathy-guidelines principle asks to avoid. Flagging this explicitly since dropping columns is a
  real, harder-to-reverse schema change — happy to keep them instead if there's a filtering need I'm
  not seeing yet.
- **`Application` gains `interview_datetime`** (nullable date/time): supports User Story 5, and gives
  Milestone 7's interview-reminder job real data to read once it's built.
- **`Application.status`'s meaningful values become**: `applied` (default, unchanged) / `shortlisted` /
  `waiting` / `selected` / `rejected` — reconciling the wireframe's dropdown (Shortlist/Waiting/Reject)
  with the Milestones doc's stated final set (Shortlisted/Selected/Rejected) by including all four
  non-default options.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A Company can go from an empty dashboard to a live, applicable Drive in one Create Drive
  submission, with zero Admin involvement beyond the one-time Company approval from Milestone 3.
- **SC-002**: Marking a Drive complete moves it from Upcoming to Closed 100% of the time, immediately.
- **SC-003**: A Company only ever sees its own Drives and Applications — 100% isolation, verified by
  attempting cross-Company access directly and confirming refusal.
- **SC-004**: Every Application status change and interview date/time set is visible correctly the next
  time that Application is viewed — no lost writes across a full pass of User Stories 4-5.
- **SC-005**: A pending or rejected Company is blocked from every capability in this milestone, 100% of
  attempts — reusing Milestone 2/3's existing approval-gate verification pattern.

## Assumptions

- "Closed Drives" → "update" opens the same Applications-review screen as an Upcoming Drive's "view
  details" (the wireframe draws no distinct destination for it) — closing a Drive stops new
  Applications, it doesn't freeze existing ones from still being decided on.
- Interview scheduling is a single date/time field on the Application, settable independently of
  status (per direct clarification) — no separate interview-slots/calendar entity in this milestone.
- The status set is Shortlisted/Waiting/Selected/Rejected (per direct clarification, merging the
  wireframe and the Milestones doc's wording) — a Company can set any of the four directly; nothing in
  this milestone requires passing through Shortlisted before reaching Selected/Rejected.
- Dropping `JobPosition`'s three structured eligibility columns in favor of one freeform
  `eligibility_criteria` field (see Key Entities) is called out explicitly above for review before
  implementation, since it's a real schema removal, not just an addition.
- "Share acceptance or rejection status... to applicants" (Milestones doc wording) means a Student can
  see their own Application's status once Milestone 5 builds their dashboard — it is not a separate
  notification/messaging action the Company takes in this milestone.
- No email/SMS notification of any kind is in scope here — Milestone 7 (Backend Jobs) is where
  asynchronous notifications belong, per the constitution's milestone-sliced delivery principle.
