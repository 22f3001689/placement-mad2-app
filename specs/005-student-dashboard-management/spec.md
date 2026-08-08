# Feature Specification: Student Dashboard & Job Application System

**Feature Branch**: `005-student-dashboard-management`

**Created**: 2026-08-02

**Status**: Draft

**Input**: Milestone 5 (per official Milestones doc) — "Student Dashboard and Job Application System
(Flask+Vue)". Students update their profile, browse Companies and their Drives, apply, track
application status (including interview schedule/mode and Company feedback), and download a placement
confirmation once placed. Backed by a provided wireframe (Student Dashboard → Organizations → Company
overview + Current Drives → Drive detail with Apply; Applied Drives / History → Student Application
History with per-row Interview/Results/Remark).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Student updates their own profile (Priority: P1)

A Student edits their own profile — branch, graduation year, CGPA, skills, contact, resume, and
photo — and the changes are visible immediately, everywhere that profile is already shown (Admin's and
Company's existing views from Milestones 3-4).

**Why this priority**: Milestone 2 only ever set a Student's `name` at registration; every other
profile field has been sitting empty or seed-only until now. Nothing else in this milestone (browsing,
applying, being reviewed) is meaningfully demoable with a blank profile.

**Independent Test**: As a Student, edit each profile field, reload, and confirm every value persisted
— then confirm Admin's existing Registered Students view (Milestone 3) shows the same data.

**Acceptance Scenarios**:

1. **Given** a Student with a mostly-empty profile, **When** they submit the edit-profile form with
   new values, **Then** every field is saved and shown correctly on reload.
2. **Given** a Student uploads a new resume or photo, **When** it's saved, **Then** the same file is
   what Admin/Company already see for that Student (reusing Milestone 3's `photo_path`/`resume_path`
   fields and static-serving approach) — no separate storage path.

---

### User Story 2 - Student browses Organizations, then a Company's ongoing Drives (Priority: P1)

The Student's dashboard lists Organizations (approved Companies); opening one shows that Company's
overview and its currently-ongoing Drives; opening a Drive shows its full detail with an Apply action.

**Why this priority**: This is the browsing path to the one action (Apply) this whole system exists
to support — without it, applying has nothing to apply *to* from the Student's own side.

**Independent Test**: As a Student, open an approved Company from Organizations, confirm its overview
and only its `ongoing` Drives appear (not `completed` ones or another Company's), then open one Drive
and confirm its full detail renders.

**Acceptance Scenarios**:

1. **Given** several approved Companies exist, **When** the Student views Organizations, **Then** only
   approved Companies appear — a pending or rejected one does not.
2. **Given** an approved Company with Drives in both `ongoing` and `completed` states, **When** the
   Student opens that Company, **Then** only its `ongoing` Drives are listed as Current Drives.
3. **Given** a Drive, **When** the Student opens its detail, **Then** it shows the same Job Title,
   Description, Salary, Location, and owning Company's logo/name that Admin and Company already see
   for it (Milestones 3-4).

---

### User Story 3 - Student applies to a Drive (Priority: P1)

From a Drive's detail screen, the Student clicks Apply and an Application is created; applying twice
to the same Drive is refused, matching the existing database constraint from Milestone 1.

**Why this priority**: The core transaction this whole milestone builds toward.

**Independent Test**: Apply to a Drive the Student hasn't applied to yet, confirm it now appears in
their own Applied Drives/History; attempt to apply again to the same Drive and confirm refusal.

**Acceptance Scenarios**:

1. **Given** an `ongoing` Drive the Student hasn't applied to, **When** they click Apply, **Then** an
   Application is created with `status="applied"`, and it now appears in their own Applied Drives.
2. **Given** a Drive the Student has already applied to, **When** they attempt to apply again,
   **Then** it's refused — one Application per Student per Drive, unchanged from Milestone 1.
3. **Given** a Drive that's already `completed`, **When** the Student attempts to apply, **Then** it's
   refused — Applying is only possible while a Drive is still `ongoing`.

---

### User Story 4 - Student tracks their own Application status, interview, and Company feedback (Priority: P1)

The Student's own Application History lists every Drive they've applied to — Job Title, Results
(their Application's status, in the same Shortlisted/Waiting/Selected/Rejected/Applied vocabulary
Company already sets from Milestone 4), how the interview will be conducted, when, and any Company
Remark left on the decision.

**Why this priority**: This is "apply and track application status" and "view interview schedules and
feedback" from the Milestones doc — the other half of the core loop alongside applying itself.

**Independent Test**: With Applications in a mix of statuses (some with an interview scheduled and a
remark, some without), load History and confirm every row shows the right status, interview info, and
remark — exactly what Company set for it in Milestone 4's own review screen.

**Acceptance Scenarios**:

1. **Given** several of the Student's own Applications, **When** they load their History, **Then**
   every one appears — no filtering, no other Student's Applications.
2. **Given** an Application with an interview date/time and mode set by the Company (Milestone 4),
   **When** the Student views it, **Then** both are shown exactly as the Company set them.
3. **Given** an Application with a Company Remark left on its decision, **When** the Student views it,
   **Then** the Remark is shown; if none was left, it shows as empty/none, not an error.

---

### User Story 5 - Student searches job postings (Priority: P2)

The Student searches across all `ongoing` Drives by Company name, Job Title/Drive Name, or required
skills, and only matching Drives are returned.

**Why this priority**: Genuinely useful once more than a handful of Drives exist, but the platform is
fully usable/demoable without it (Organizations browsing already reaches every Drive) — same reasoning
Milestone 3's Admin search got P2.

**Independent Test**: With several ongoing Drives across different Companies, search a term matching
only one and confirm only that one returns; search a term matching none and confirm an empty result,
not an error.

**Acceptance Scenarios**:

1. **Given** several ongoing Drives, **When** the Student searches by Company name, Job Title, or a
   required skill, **Then** only Drives matching that substring on the relevant field are returned.
2. **Given** a search term matching no Drive, **When** the Student searches, **Then** the result is
   empty, not an error.

---

### User Story 6 - Student downloads a placement confirmation (Priority: P3)

Once a Student has a `Placement` record (created however Milestone 1's model already anticipates —
today, only via direct database action; a real Company-side "finalize placement" flow is out of scope
here), they can download a confirmation of it.

**Why this priority**: Named directly in the Milestones doc ("Download offer letters or placement
confirmations"), but it's the last step of an already-rare event (an actual placement) — everything
else in this milestone matters regardless of whether anyone's been placed yet.

**Independent Test**: With a seeded `Placement` record for the Student, download the confirmation and
confirm it contains that Placement's position title, salary, and joining date.

**Acceptance Scenarios**:

1. **Given** a Student with a `Placement` record, **When** they download their confirmation, **Then**
   it contains that Placement's position, company, salary, and joining date.
2. **Given** a Student with no `Placement` record, **When** they look for a confirmation to download,
   **Then** none is offered — not an error, just nothing to download yet.

---

### Edge Cases

- What happens if a Company is blacklisted (Milestone 3) after a Student already applied to one of its
  Drives? The Application is untouched (Milestone 3's existing behavior) — it still shows in the
  Student's History with whatever status it already had.
- What happens if a Student tries to view or apply to a Drive belonging to a Company that isn't
  approved? Can't happen through Organizations (User Story 2, Scenario 1 already excludes non-approved
  Companies), and direct access to such a Drive's Apply action is refused the same way.
- What happens if the Company later changes an Application's status/remark/interview info after the
  Student has already viewed it once? The Student sees the updated values the next time they load
  History — there's no notification, just an up-to-date read.
- What happens to search if the search term is empty? Returns every `ongoing` Drive, same as no filter
  — not an error, not an empty result (same convention as Milestone 3's search).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let a Student update their own profile — branch, graduation year, CGPA,
  skills, contact, resume, and photo.
- **FR-002**: System MUST let a Student list Organizations (approved Companies only) and view one
  Company's overview and its `ongoing` Drives.
- **FR-003**: System MUST let a Student view one Drive's full detail — Job Title, Description,
  Eligibility Criteria, Salary, Location, and owning Company's logo/name — so applying is an informed
  choice, given eligibility is self-attested (see Assumptions).
- **FR-004**: System MUST let a Student apply to an `ongoing` Drive they haven't already applied to,
  creating an Application with `status="applied"`.
- **FR-005**: System MUST refuse a second Application by the same Student to the same Drive.
- **FR-006**: System MUST refuse an Application to a Drive that is `completed`.
- **FR-007**: System MUST let a Student list every one of their own Applications with its current
  status, interview date/time, interview mode, and any Company Remark — and refuse this for anyone
  else's Applications.
- **FR-008**: System MUST let a Student search `ongoing` Drives by a substring match on Company name,
  Job Title/Drive Name, or required skills.
- **FR-009**: System MUST let a Student download a placement confirmation if a `Placement` record
  exists for them, containing its position, company, salary, and joining date.
- **FR-010**: System MUST refuse every capability in this milestone to any caller that isn't logged in
  as the owning Student, per the role check already established in Milestone 2.
- **FR-011**: System MUST let a Company filter its Drive's Applicants list by status and sort it by
  status (extending Milestone 4's existing Applicants-list endpoint) — the cheap alternative to
  automatic eligibility rejection (see Assumptions) for making shortlisting faster.

### Key Entities

- **`Application` gains `interview_mode`** (e.g. `"in_person"` / `"virtual"`), alongside the existing
  `interview_datetime` from Milestone 4 — the wireframe's History screen shows both as distinct
  columns, not one combined value.
- **`Application` gains `company_remark`** (freeform text, nullable) — closes a gap in Milestone 4's
  own scope (its Milestones-doc wording said "shortlist or reject applicants with feedback," but no
  feedback field was ever added). Milestone 4's existing decision endpoint gains an optional remark
  alongside the status it already sets; this milestone is where a Student first reads it.
- **`Company` gains `overview`** (freeform text, nullable) — the wireframe's Company-detail screen
  shows an about-us-style paragraph that doesn't exist on the model today. Setting/editing it is out
  of scope for both this milestone and Milestone 4 (Company has no general profile-editing flow yet,
  only Drive management) — for now it's populated the same way `logo_path` already is: seeded, not
  self-service.
- No other new entities. Reuses `Student` (Milestone 1/3), `Company`/`JobPosition`/`Application`
  (Milestones 1/3/4), and `Placement` (Milestone 1, already modeled but never yet populated by any
  in-app flow).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A Student's profile edit is visible in Admin's Registered Students view (Milestone 3)
  immediately after saving, with zero manual sync step.
- **SC-002**: Organizations only ever shows approved Companies, and a Company's Current Drives only
  ever shows its own `ongoing` Drives — 100% across a full pass of User Story 2's scenarios.
- **SC-003**: Applying twice to the same Drive is refused 100% of the time; applying to a `completed`
  Drive is refused 100% of the time.
- **SC-004**: Every value a Company sets on an Application in Milestone 4's review screen (status,
  interview date/time, interview mode, remark) is visible to the Student exactly as set, the next time
  they load History.
- **SC-005**: Every search returns exactly the Drives matching the given term on the specified fields —
  no false positives, no missed matches.
- **SC-006**: A Student with a `Placement` record can download a confirmation containing the correct
  position/company/salary/joining-date; a Student without one is offered nothing to download, not an
  error.

## Assumptions

- No Company-side "finalize a Placement" flow exists yet — `Placement` records are still only created
  directly (as Milestone 1's own seed data already does), not through any UI this milestone or
  Milestone 4 built. User Story 6 is scoped to *downloading* an existing Placement's confirmation, not
  creating one. A real "Company marks a Student as finally placed" flow is a reasonable candidate for a
  later milestone, not invented here.
- The placement confirmation is a simple generated document (e.g. plain text or minimal HTML response
  with a download disposition) — not a designed PDF. Nothing in either source document asks for a
  particular format, and adding a PDF-generation dependency for a class project's one document type
  would be exactly the kind of unrequested complexity the constitution's simplicity principle warns
  against.
- `interview_mode`'s exact allowed values (e.g. `in_person`/`virtual`) are a small fixed set set by the
  Company (extending Milestone 4's own decision screen) — this milestone only reads and displays it.
- `Company.overview` is seeded, not Company-self-edited, in this milestone — see Key Entities. A
  Company profile-editing screen is out of scope until a milestone actually asks for one.
- "View and search job postings by company, position, or required skills" (Milestones doc wording) is
  read as searching only `ongoing` Drives — a Student has no reason to search `completed` ones, since
  they can't apply to them anyway.
- Eligibility stays self-attested — no server-side rejection at Apply time (constitution v1.2.0). Two
  cheaper alternatives are in scope instead of automatic validation: showing `eligibility_criteria` on
  the Drive detail so a Student applies with informed judgment (FR-003), and letting Company filter/
  sort its Applicants list by status (FR-011) so shortlisting is faster without needing the system to
  guess who's eligible from freeform text. Real validation (e.g. parsing/matching structured criteria)
  is deferred, not ruled out — a reasonable candidate once there's a concrete need for it.
