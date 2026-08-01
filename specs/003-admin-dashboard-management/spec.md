# Feature Specification: Admin Dashboard & Management

**Feature Branch**: `003-admin-dashboard-management`

**Created**: 2026-08-01

**Status**: Draft

**Input**: Milestone 3 (per official Milestones doc) — "Admin Dashboard and Management (Flask+Vue)".
Admin sees a dashboard of totals (students, companies, job postings, applications); approves/removes
Company profiles; approves/removes job postings (placement drives) created by Companies; searches
companies (by name/industry) and students (by name/ID/contact); views and manages all job postings and
applications; blacklists/deactivates companies and students.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin sees the state of the whole platform at a glance (Priority: P1)

The Admin logs in and immediately sees how many Students, Companies, Job Postings, and Applications
exist in the system right now.

**Why this priority**: This is the Admin's landing page and the cheapest possible slice to deliver —
it needs nothing beyond counting rows already created in Milestones 1–2, and it gives the Admin (and
whoever's grading this) an instant, verifiable signal that the dashboard is real.

**Independent Test**: Log in as Admin, view the dashboard, and confirm the four counts match what a
direct count of the database tables shows.

**Acceptance Scenarios**:

1. **Given** any number of Students, Companies, Job Postings, and Applications in the system, **When**
   Admin opens the dashboard, **Then** it shows the current total count of each, matching the database.
2. **Given** a brand-new Student, Company, Job Posting, or Application is created after the dashboard
   was last loaded, **When** Admin reloads the dashboard, **Then** the counts reflect the new totals.

---

### User Story 2 - Admin approves or rejects a Company so the approval gate from Milestone 2 means something (Priority: P1)

The Admin sees every Company account waiting for a decision and can approve or reject each one; an
approved Company can now use its company-only capabilities, and a rejected one stays blocked.

**Why this priority**: Milestone 2 built the pending/approved gate but nothing to act on it — until
this exists, every Company is stuck pending forever and Milestone 4's company-facing work can't be
demoed end-to-end.

**Independent Test**: Register a new Company (still pending from Milestone 2), have Admin approve it,
and confirm the Company can now use a company-only capability; register a second Company and reject it,
confirming it stays blocked.

**Acceptance Scenarios**:

1. **Given** a Company account with pending approval, **When** Admin approves it, **Then** its approval
   status becomes approved and its company-only capabilities unlock immediately.
2. **Given** a Company account with pending approval, **When** Admin rejects it, **Then** its approval
   status becomes rejected and it stays blocked from company-only capabilities, the same as pending.
3. **Given** a Company Admin has already approved or rejected, **When** Admin changes the decision
   later, **Then** the new decision takes effect immediately (approval is not a one-way action).

---

### User Story 3 - Admin approves or rejects a Job Posting before Students can see it (Priority: P2)

The Admin reviews Job Postings submitted by Companies and approves or rejects each one; only approved
postings are meant to be visible to Students once Milestone 5 builds that view.

**Why this priority**: This mirrors Company approval but one layer down, and depends on at least one
approved Company existing to post something — it's the natural next slice after User Story 2, and it
has to exist before Milestone 5 can assume "visible postings are vetted."

**Independent Test**: With an approved Company's Job Posting sitting pending, have Admin approve it and
confirm its status changes to approved; post a second one and reject it, confirming its status becomes
rejected.

**Acceptance Scenarios**:

1. **Given** a pending Job Posting from an approved Company, **When** Admin approves it, **Then** its
   status becomes approved.
2. **Given** a pending Job Posting, **When** Admin rejects it, **Then** its status becomes rejected and
   it is not treated as an active posting.

---

### User Story 4 - Admin finds a specific Company or Student without scrolling through everything (Priority: P2)

The Admin searches Companies by name or industry, and searches Students by name, ID, or contact, and
gets back just the matching accounts.

**Why this priority**: Once even a modest number of test accounts exist, an unfiltered list becomes
unusable for grading/demo purposes — this is a straightforward, independently testable slice that makes
every other Admin capability easier to use, but nothing else depends on it existing first.

**Independent Test**: With several Companies and Students seeded, search by a term matching only one of
them and confirm only that one comes back; search by a term matching none and confirm an empty result,
not an error.

**Acceptance Scenarios**:

1. **Given** several Company accounts, **When** Admin searches by a name or industry substring, **Then**
   only Companies whose name or industry contains that substring are returned.
2. **Given** several Student accounts, **When** Admin searches by a name, ID, or contact substring,
   **Then** only Students matching that substring on any of those fields are returned.
3. **Given** a search term matching no one, **When** Admin searches, **Then** the result is an empty
   list, not an error.

---

### User Story 5 - Admin can see and act on every Job Posting and Application in the system, not just pending ones (Priority: P2)

Beyond the pending-approval queue from User Story 3, the Admin can browse every Job Posting (any status)
and every Application (any status) across all Companies and Students, and can take the same actions on
it as via the queue.

**Why this priority**: Approval queues only ever show what's currently pending; oversight requires
seeing the full picture (approved, rejected, closed postings; every application regardless of student or
company) — this is what makes Milestone 3 an actual management view and not just a two-item approval
inbox.

**Independent Test**: With Job Postings and Applications in a mix of statuses, load the all-postings and
all-applications views and confirm every record appears with its real current status, not just the
pending ones.

**Acceptance Scenarios**:

1. **Given** Job Postings in a mix of statuses (pending, approved, rejected), **When** Admin views all
   Job Postings, **Then** every one appears, tagged with its actual status.
2. **Given** Applications across multiple Students and Companies, **When** Admin views all Applications,
   **Then** every one appears, regardless of which Student or Company it belongs to.

---

### User Story 6 - Admin blacklists a Company or Student that's misbehaving, and can undo it (Priority: P3)

The Admin deactivates a Company's or Student's account outright, blocking it from logging in at all
(reusing the same deactivation Milestone 2 already enforces at login), and can reactivate it later.

**Why this priority**: This is a stronger, less frequently needed action than approval/rejection — it's
valuable but the platform is fully usable for grading/demo purposes without it, so it's the last slice.

**Independent Test**: Deactivate an active Company or Student account and confirm a subsequent login
attempt with correct credentials is refused (per Milestone 2's existing deactivation check); reactivate
it and confirm login succeeds again.

**Acceptance Scenarios**:

1. **Given** an active Company or Student account, **When** Admin deactivates it, **Then** it can no
   longer log in, even with the correct password.
2. **Given** a deactivated Company or Student account, **When** Admin reactivates it, **Then** it can
   log in normally again.
3. **Given** the one Admin account, **When** anyone attempts to deactivate it, **Then** the action is
   refused — there is no path in this milestone to lock out the only Admin.

---

### Edge Cases

- What happens if Admin tries to approve/reject a Company or Job Posting that doesn't exist (bad ID)?
  The action is refused with a clear "not found," nothing is changed.
- What happens if Admin approves a Job Posting belonging to a Company that isn't itself approved? This
  should not normally be possible since posting is a company-only capability gated on approval
  (Milestone 4), but if it happens anyway, the Job Posting approval succeeds independently of Company
  status — Admin should re-check the Company separately; adding a defensive check here is out of scope.
- What happens to Job Postings and Applications belonging to a Company that Admin later deactivates?
  They are left exactly as they are — deactivation blocks future login and future company-only actions,
  it does not touch existing records.
- What happens if a search term is empty? It returns every Company or Student, exactly like no filter
  was applied — not an error and not an empty result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST show Admin a dashboard with the current total count of Students, Companies,
  Job Postings, and Applications.
- **FR-002**: System MUST let Admin list every Company account whose approval is pending.
- **FR-003**: System MUST let Admin approve a Company, immediately unlocking its company-only
  capabilities.
- **FR-004**: System MUST let Admin reject a Company, keeping its company-only capabilities blocked the
  same way pending does.
- **FR-005**: System MUST let Admin change a Company's approval decision again later (approve after
  rejecting, or vice versa).
- **FR-006**: System MUST let Admin list every Job Posting whose approval is pending.
- **FR-007**: System MUST let Admin approve or reject a Job Posting, and that decision MUST be reflected
  the next time anyone reads that posting's status.
- **FR-008**: System MUST let Admin search Companies by a substring match on name or industry.
- **FR-009**: System MUST let Admin search Students by a substring match on name, ID, or contact.
- **FR-010**: System MUST let Admin view every Job Posting in the system regardless of status, and every
  Application in the system regardless of which Student or Company it belongs to.
- **FR-011**: System MUST let Admin deactivate an active Company or Student account, and reactivate a
  deactivated one, without touching that account's existing Job Postings, Applications, or Placements.
- **FR-012**: System MUST refuse any attempt to deactivate the Admin account.
- **FR-013**: System MUST refuse every Admin action in this milestone (approve/reject/search/deactivate)
  to any caller that isn't logged in as Admin, per the role check already established in Milestone 2.

### Key Entities

- No new entities. This milestone only adds Admin-facing operations over Milestone 1's existing
  `Company.approval_status` (now also usable as "rejected", not just "pending"/"approved"),
  `JobPosition.status` (now also usable as "approved"/"rejected", not just its "pending" default), and
  `User.is_active` (already used by Milestone 2's login check; this milestone adds the Admin action that
  flips it).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Admin's dashboard counts always match a direct count of the underlying tables, with no
  caching lag introduced in this milestone (real-time caching arrives later, in Milestone 8).
- **SC-002**: A newly registered Company goes from pending to a working company-only capability in a
  single Admin approval action, with no other manual step.
- **SC-003**: Every Company or Student search returns exactly the accounts matching the given term on
  the specified fields — no false positives, no missed matches, across a full pass of the User Story 4
  scenarios.
- **SC-004**: Admin can see 100% of Job Postings and Applications in the system through the "view all"
  capability, not just whatever is currently pending.
- **SC-005**: A deactivated Company or Student cannot log in, verified the same way Milestone 2 verified
  it (SC-005 there) — 100% of attempts rejected regardless of password correctness.
- **SC-006**: The Admin account can never be deactivated, across every attempt to do so.

## Assumptions

- "Approve and Remove Company profiles" / "Approve and Remove job posting/placement drives" (Milestone
  doc wording) is read as **approve/reject via status field**, not permanent deletion. Milestone 1's
  data model deliberately avoids cascading deletes from Company/JobPosition into Applications and
  Placements so that history survives (see `specs/001-database-models-schema/data-model.md`); a hard
  delete here would either violate that guarantee or leave orphaned rows. "Remove" a Company means
  reject it (status becomes "rejected"); "Remove" a Job Posting means reject it the same way. The
  separate "Blacklist/Deactivate" bullet already covers the stronger, account-level lockout action, so
  reading "Remove" as reject (not delete) doesn't lose any capability the milestone doc asks for.
- Deactivating a Company or Student is reusing Milestone 2's existing `is_active` flag and its
  already-built login check — this milestone only needs to add the Admin-facing action that flips it,
  not any new enforcement logic.
- "Search companies (by name/industry)" and "Search students (by name/ID/contact)" are simple substring
  matches on those fields, not fuzzy search or full-text search — nothing in either source document asks
  for more.
- "View and manage all job postings and applications" reuses the same approve/reject action as the
  pending-queue views (User Stories 2–3); it's a broader read (every status, not just pending) over the
  same underlying data, not a separate management capability.
- No new Company/Student self-service actions are in scope here — this milestone is entirely
  Admin-facing. Company's and Student's own dashboards are Milestones 4 and 5.
