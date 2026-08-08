# Feature Specification: Job Application History and Status Tracking

**Feature Branch**: `006-application-history-status`

**Created**: 2026-08-08

**Status**: Draft

**Input**: User description: "Milestone 6: Job Application History and Status Tracking (Flask+Vue). Store and display complete application and placement history. Prevent duplicate applications for the same job posting. Ensure only approved companies can create placement drives. Ensure students can view and apply only to approved placement drives. Maintain status updates (Applied / Shortlisted / Interview / Offer / Rejected / Placed). Admin and Company can view student profiles and applications; Students can view their own records."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Company moves an application through the full status lifecycle (Priority: P1)

A Company reviews an applicant and moves them through Applied → Shortlisted → Interview → Offer → Placed (or → Rejected at any point). When the Company marks an application as Placed, the system records the placement outcome (position, salary, joining date) so it becomes part of the Student's permanent placement history — without the Company needing a separate step.

**Why this priority**: This is the core of the milestone — today the Company can only reach "selected," and no code path anywhere ever creates the placement record a Student's confirmation download depends on. Nothing else in this milestone is useful until statuses reliably drive real placement history.

**Independent Test**: As a Company, move one applicant's status all the way to Placed and confirm a Placement row appears with matching student/company/position, and the Student's placement confirmation download now succeeds.

**Acceptance Scenarios**:

1. **Given** an application with status Applied, **When** the Company sets it to Shortlisted, then Interview, then Offer, **Then** each transition succeeds and the Student sees the updated status and any interview date/mode already scheduled.
2. **Given** an application with status Offer, **When** the Company sets it to Placed and supplies position title, salary, and joining date, **Then** a Placement record is created linking the Student, Company, and Application, and the Student can now download a placement confirmation.
3. **Given** an application in any non-final status, **When** the Company sets it to Rejected, **Then** the application is marked Rejected and no Placement record is created.
4. **Given** an application already Placed, **When** anyone attempts to change its status again, **Then** the system rejects the change (a placement outcome is final).

---

### User Story 2 - Student views complete application and placement history in one place (Priority: P1)

A Student wants a single view of everything that has happened across every drive they've applied to — status, interview details, company remarks — plus, once placed, their placement outcome.

**Why this priority**: Directly required by the milestone ("Students can view their own records") and is the natural companion to Story 1 — the history is only meaningful once statuses and placement are wired up correctly.

**Independent Test**: As a Student with at least one application in each status, open the history view and confirm every application appears with correct status, interview info, and (for Placed) placement details, without needing to open each drive individually.

**Acceptance Scenarios**:

1. **Given** a Student has applied to multiple drives with different statuses, **When** they open their application history, **Then** every application is listed with its current status, company/job title, interview date/mode (if scheduled), and company remark (if any).
2. **Given** a Student has been Placed, **When** they view their history, **Then** the placement outcome (company, position, salary, joining date) is visible alongside the corresponding application.

---

### User Story 3 - Admin and Company can view a Student's full profile (Priority: P2)

An Admin or a Company reviewing an applicant wants to see the Student's complete profile (branch, graduation year, CGPA, skills, contact, resume/photo) in one place, not just the fields currently surfaced inline on the application-review screen.

**Why this priority**: Required by the milestone ("Admin and Company can view student profiles"). Lower priority than Stories 1–2 because a usable subset of this (CGPA, skills, branch) already exists on the Company's application-review screen from Milestone 5 — this closes the remaining gap (Admin has none at all; Company's view is missing graduation year/contact) rather than building from zero.

**Independent Test**: As an Admin, open a Student's profile from the Students list and confirm all profile fields are visible. As a Company, open an applicant's profile from an application and confirm the same.

**Acceptance Scenarios**:

1. **Given** an Admin is viewing the Students list, **When** they select a Student, **Then** they see that Student's full profile (name, branch, graduation year, CGPA, skills, contact, resume/photo links) and their full application history.
2. **Given** a Company is reviewing an application, **When** they view the applicant, **Then** they see the same full profile fields (not just CGPA/branch/skills as today).

---

### User Story 4 - Students only ever see and apply to drives from currently-approved companies (Priority: P2)

If a Company's approval is revoked after it has posted drives, those drives must stop being visible/appliable to Students immediately — approval is a live gate, not a one-time check at drive-creation time.

**Why this priority**: Explicitly called out by the milestone ("ensure students can view and apply only to approved placement drives") and is a real, currently-unenforced gap: drive creation already requires an approved company, but drive *visibility* to students does not re-check approval.

**Independent Test**: As an Admin, revoke an already-approved Company's approval after it has posted an ongoing drive. Confirm that drive disappears from the Student's organization/drive listing and a direct apply attempt is rejected.

**Acceptance Scenarios**:

1. **Given** a Company with ongoing drives has its approval revoked, **When** a Student lists organizations or drives, **Then** that Company and its drives no longer appear.
2. **Given** a Student already had a drive's detail page open before the Company's approval was revoked, **When** they attempt to apply, **Then** the system rejects the application.
3. **Given** a Student already applied and was placed before the Company's approval was revoked, **When** they view their history, **Then** that application/placement record is still visible (history is never hidden retroactively).

### Edge Cases

- Duplicate applications to the same drive by the same Student are already prevented at the database level (Milestone 1) — this milestone re-verifies that guarantee rather than re-implementing it.
- An application cannot be changed away from Placed or Rejected once set (both are final outcomes); this prevents an accidental double placement or an un-rejection that bypasses the normal flow.
- Revoking a Company's approval never deletes or hides its Companies' existing Applications/Placements from Student, Admin, or Company history views — only *new* visibility/actions (browsing, applying) for Students are gated live.
- The `waiting` status used in the current codebase is retired; existing rows with `waiting` are migrated to `Interview`, and existing rows with `selected` are migrated to `Offer` (see Assumptions).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support exactly six application statuses: Applied, Shortlisted, Interview, Offer, Rejected, Placed.
- **FR-002**: The system MUST allow a Company to move an application it owns from any non-final status to any other non-final status, or to Rejected, or (only from Offer) to Placed.
- **FR-003**: The system MUST reject any attempt to change the status of an application that is already Placed or Rejected.
- **FR-004**: The system MUST, when an application's status is set to Placed, require and record a position title, salary, and joining date, and create a corresponding placement record for that Student/Company/Application at that moment.
- **FR-005**: The system MUST continue to prevent more than one application by the same Student to the same job posting.
- **FR-006**: The system MUST continue to prevent a Company from creating a drive unless that Company is currently approved.
- **FR-007**: The system MUST exclude drives belonging to a currently-unapproved Company from every Student-facing listing and detail view, and MUST reject a Student's attempt to apply to such a drive.
- **FR-008**: The system MUST allow a Student to view a single, complete history of all their own applications, including current status, interview details (if scheduled), company remark (if any), and placement outcome (if placed).
- **FR-009**: The system MUST allow an Admin to view any Student's full profile (name, branch, graduation year, CGPA, skills, contact, resume/photo) and that Student's full application history.
- **FR-010**: The system MUST allow a Company to view the full profile (same fields as FR-009) of any Student who has applied to one of its drives.
- **FR-011**: The system MUST migrate existing application rows with status `waiting` to `Interview` and rows with status `selected` to `Offer`, with no data loss and no automatic creation of placement records for this migration.

### Key Entities

- **Application** (existing entity, status vocabulary changes): now carries one of exactly six statuses (Applied/Shortlisted/Interview/Offer/Rejected/Placed) instead of the prior five; Placed and Rejected are terminal.
- **Placement** (existing entity, now actually populated by the app): created automatically the moment an Application transitions to Placed, carrying position title, salary, and joining date at that time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A Company can take an applicant from Applied to Placed, and the Student can immediately download a placement confirmation reflecting that outcome, with zero manual/offline steps outside the app.
- **SC-002**: 100% of a Student's past applications (across all statuses) are visible from a single history view, with no need to open each drive individually to see current status.
- **SC-003**: Revoking a Company's approval removes its drives from Student-facing views within the same session (no stale visibility), while never removing that Company's existing applicants' history.
- **SC-004**: An Admin or Company can view any Student's full profile in at most one navigation step from that Student's name/application.

## Assumptions

- The "waiting" status in the current implementation represented "decision pending, possibly interview-related" and is superseded by `Interview` in the new vocabulary; existing rows are migrated accordingly (per user decision).
- The "selected" status in the current implementation never created a Placement record and represented "chosen by company, not yet finalized"; it is treated as equivalent to `Offer`, not `Placed`, and migrated accordingly (per user decision) — no retroactive Placement rows are created for pre-existing data.
- Placed is reached only by direct Company action (Company sets the status to Placed and supplies placement details); no separate Student-side "accept offer" step is introduced in this milestone (per user decision).
- "Approved" for FR-007 means the Company's current `approval_status`, checked live on every Student-facing read/write, not the approval status at the time the drive or Company was created.
- Interview scheduling (date/time/mode) remains a property attached to an Application regardless of its status, as it already is today; this milestone does not change how interviews are scheduled, only the status vocabulary around them.
