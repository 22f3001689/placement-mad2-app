# Feature Specification: Admin Dashboard & Management

**Feature Branch**: `003-admin-dashboard-management`

**Created**: 2026-08-01

**Status**: Draft

**Input**: Milestone 3 (per official Milestones doc) — "Admin Dashboard and Management (Flask+Vue)".
Redesigned as a single-page dashboard per direct product clarification: **Section 1** — a welcome
header, live totals, and one search bar that searches Companies and Students together. **Section 2** —
five subsections: Registered Companies (blacklist/whitelist), Registered Students
(blacklist/whitelist), Company Applications (approve/reject pending Companies), Ongoing Drives (view
details, mark complete), Student Applications (read-only view).

Business-flow clarification that shapes this spec: **Admin approval gates a Company's ability to
create Drives at all** — once approved, a Company self-manages its own Drives end-to-end (create,
accept Applications, mark complete) with no further per-Drive Admin approval. Admin's role over Drives
in this milestone is oversight (view + mark complete), not gatekeeping.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin approves or rejects a Company so it can start creating Drives (Priority: P1)

The Admin sees every Company account waiting for a decision in the "Company Applications" subsection
and can approve or reject each one with one click. Approving is what actually unlocks a Company's
ability to create Drives — there's no further per-Drive approval after this.

**Why this priority**: Until this exists, every Company is stuck pending forever and Milestone 4's
"Company creates a Drive" work has nothing to build on.

**Independent Test**: Register a new Company (pending from Milestone 2), approve it from Company
Applications, and confirm it now shows up as a Registered Company rather than a pending one; reject a
second Company and confirm it never appears as Registered.

**Acceptance Scenarios**:

1. **Given** a Company account with pending approval, **When** Admin clicks Approve in Company
   Applications, **Then** its approval status becomes approved and it moves into Registered Companies.
2. **Given** a Company account with pending approval, **When** Admin clicks Reject in Company
   Applications, **Then** its approval status becomes rejected and it never appears in Registered
   Companies.
3. **Given** a rejected Company, **When** anyone looks at Company Applications afterward, **Then** it
   no longer appears there either — it isn't stuck showing as pending once decided.

---

### User Story 2 - Admin blacklists or whitelists a Company or Student (Priority: P1)

In Registered Companies and Registered Students, each row has a single toggle button — labeled
Blacklist when the account is active, Whitelist when it's already blacklisted — with a color that
reflects the current state. Clicking it flips that account's ability to log in.

**Why this priority**: This is the strongest oversight tool over already-enrolled accounts and it
reuses Milestone 2's existing deactivation check directly — cheap to deliver, high value.

**Independent Test**: Blacklist an active Company or Student, confirm its login is now refused (per
Milestone 2's existing deactivated-account check), then Whitelist it and confirm login works again.

**Acceptance Scenarios**:

1. **Given** an active, registered Company or Student, **When** Admin clicks Blacklist on its row,
   **Then** it can no longer log in, even with the correct password, and the button now reads Whitelist.
2. **Given** a blacklisted Company or Student, **When** Admin clicks Whitelist on its row, **Then** it
   can log in again, and the button now reads Blacklist.
3. **Given** the one Admin account, **When** anyone attempts to blacklist it, **Then** the action is
   refused — there is no path in this milestone to lock out the only Admin.

---

### User Story 3 - Admin searches Registered Companies and Students from one search bar (Priority: P2)

The Admin types into the one search field in Section 1 and clicks Search; both Registered Companies
(matched on name or industry) and Registered Students (matched on name, username, or contact) filter
down to whatever matches.

**Why this priority**: Once even a modest number of accounts exist, scrolling both lists unfiltered
becomes unusable for demo/grading purposes — independently valuable, but nothing else depends on it.

**Independent Test**: With several Registered Companies and Students, search a term matching only one
of them and confirm only that one shows in its respective list; search a term matching none and confirm
an empty list, not an error, in both.

**Acceptance Scenarios**:

1. **Given** several Registered Companies, **When** Admin searches a name/industry substring, **Then**
   Registered Companies narrows to only matches; Registered Students narrows the same way independently.
2. **Given** a search term matching nobody, **When** Admin searches, **Then** both lists show empty,
   not an error.
3. **Given** the search field is cleared, **When** Admin searches (or reloads), **Then** both lists show
   every Registered Company/Student again, unfiltered.

---

### User Story 4 - Admin oversees Ongoing Drives and marks them complete (Priority: P2)

The "Ongoing Drives" subsection lists every Drive that isn't finished yet — Serial Number, Drive Name,
a View Details action that opens a read-only modal with the Drive's full information, and a Mark as
Complete action that closes it out.

**Why this priority**: This is Admin's oversight window into Company-run Drives once Milestone 4 lets
Companies create them — it depends conceptually on Drives existing, but this milestone's own
verification seeds one directly so the capability can be demoed now.

**Independent Test**: With an ongoing Drive, open its View Details modal and confirm the full
information shows; click Mark as Complete and confirm it disappears from Ongoing Drives.

**Acceptance Scenarios**:

1. **Given** a Drive that is ongoing, **When** Admin clicks View Details, **Then** a read-only modal
   shows that Drive's full information (title, description, eligibility, deadline, owning Company).
2. **Given** an ongoing Drive, **When** Admin clicks Mark as Complete, **Then** its status becomes
   completed and it no longer appears in Ongoing Drives.
3. **Given** a Drive already marked complete, **When** anyone looks at Ongoing Drives afterward,
   **Then** it stays gone — completing is not reversible from this milestone's UI.

---

### User Story 5 - Admin reviews every Student Application, read-only (Priority: P3)

The "Student Applications" subsection lists every Application in the system — Serial Number, Student
Name, Drive, Company, Date, and a View action opening a read-only modal with that Application's detail.
Admin cannot change anything from this view; it's oversight, not a decision point.

**Why this priority**: Valuable visibility, but the platform's core loop (Company approval → Drive
oversight) is fully demoable without it, so it's the last slice.

**Independent Test**: With several Applications across different Students and Companies, load Student
Applications and confirm every one appears with correct details; open one's View modal and confirm the
details match.

**Acceptance Scenarios**:

1. **Given** Applications from multiple Students and Companies, **When** Admin loads Student
   Applications, **Then** every one appears, in order, none filtered out.
2. **Given** any row in Student Applications, **When** Admin clicks View, **Then** a read-only modal
   shows that Application's Student, Drive, Company, Date, and current status — with no action
   available to change it.

---

### Edge Cases

- What happens if Admin tries to approve/reject a Company, or complete a Drive, that doesn't exist
  (bad ID)? The action is refused with a clear "not found," nothing is changed.
- What happens to a Company's own Drives if Admin later blacklists that Company? They are left exactly
  as they are — blacklisting blocks future login, it does not touch existing Drives, Applications, or
  Placements.
- What happens if the search field is empty and Search is clicked anyway? It behaves exactly like no
  filter was applied — returns everyone, not an error and not an empty result.
- What happens to a rejected Company later — can Admin revisit and approve it? Out of scope for this
  milestone's UI: Company Applications only ever shows accounts still pending, so a decision (either
  direction) is final from the dashboard's point of view. Reversing one would require direct database
  access, not a supported action here.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST show Admin live totals of Students, Companies, Drives, and Applications.
- **FR-002**: System MUST let Admin list every Company account whose approval is still pending, in a
  Company Applications view.
- **FR-003**: System MUST let Admin approve a Company from that view, moving it into Registered
  Companies and unlocking its ability to create Drives.
- **FR-004**: System MUST let Admin reject a Company from that view, after which it appears in neither
  Company Applications nor Registered Companies.
- **FR-005**: System MUST let Admin list every approved (Registered) Company and every Student, each
  with its current active/blacklisted state.
- **FR-006**: System MUST let Admin blacklist an active Company or Student account, immediately
  blocking its login per Milestone 2's existing deactivation check.
- **FR-007**: System MUST let Admin whitelist a blacklisted Company or Student account, immediately
  restoring its ability to log in.
- **FR-008**: System MUST refuse any attempt to blacklist the Admin account.
- **FR-009**: System MUST let Admin search Registered Companies by a substring match on name or
  industry, and Registered Students by a substring match on name, username, or contact, from one
  search action.
- **FR-010**: System MUST let Admin list every Drive that is not yet completed (Ongoing Drives), and
  view any one Drive's full detail on demand.
- **FR-011**: System MUST let Admin mark an ongoing Drive as completed, after which it no longer
  appears in Ongoing Drives.
- **FR-012**: System MUST let Admin list every Application in the system and view any one's detail —
  read-only, with no state-changing action available from this view.
- **FR-013**: System MUST refuse every Admin action in this milestone to any caller that isn't logged
  in as Admin, per the role check already established in Milestone 2.

### Key Entities

- No new entities. This milestone reuses Milestone 1's `Company.approval_status` (unchanged:
  "pending"/"approved"/"rejected") and `User.is_active` (unchanged, already enforced at login).
- **Changed meaning, same column**: `JobPosition.status` ("Drive" in this UI) no longer models an
  Admin-approval workflow. Per the business-flow clarification above, only two values are meaningful
  from this milestone forward: `"ongoing"` (default — a Company's Drive is open for Applications the
  moment it exists) and `"completed"` (set only by the Mark as Complete action). The
  "pending"/"approved"/"rejected" values Milestone 1 anticipated for this column are not used going
  forward.
- **New fields on existing entities** (post-review addition, no new tables): `Company.logo_path`,
  `Student.photo_path` (alongside Milestone 1's existing `Student.resume_path`), and
  `JobPosition.location`. All nullable strings holding a path under `app/static/uploads/`; there is no
  upload flow yet, so these are seeded directly (see Assumptions).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Admin's totals always match a direct count of the underlying tables — specifically, the
  Companies total matches the count of Companies actually listed in Registered Companies (i.e. only
  `approved` ones), not a raw count of every Company row regardless of status.
- **SC-002**: A newly registered Company goes from pending to appearing in Registered Companies (and
  able to create Drives, once Milestone 4 exists) in a single Admin approval action.
- **SC-003**: A rejected Company never appears in Registered Companies and drops out of Company
  Applications immediately.
- **SC-004**: Every search returns exactly the Companies/Students matching the given term on the
  specified fields — no false positives, no missed matches, across a full pass of User Story 3.
- **SC-005**: A blacklisted Company or Student cannot log in, 100% of attempts, verified the same way
  Milestone 2 verified its deactivation check.
- **SC-006**: The Admin account can never be blacklisted, across every attempt to do so.
- **SC-007**: Marking a Drive complete removes it from Ongoing Drives 100% of the time, immediately.
- **SC-008**: Every Application in the system appears in Student Applications — 100% coverage, verified
  by comparing the list's count to a direct table count.

## Assumptions

- The dashboard totals (FR-001) are shown in Section 1 alongside the "Welcome Admin" header and search
  bar, even though they weren't explicitly called out in the single-page mockup — the official
  Milestones doc requires them, and they fit there without disrupting the described layout.
- The Companies total counts only `approved` Companies, matching Registered Companies exactly — a
  pending or rejected Company is not counted, since showing a total that doesn't match any visible list
  on the page is confusing rather than informative (corrected after initial review: the first
  implementation counted every Company row regardless of status, which visibly disagreed with
  Registered Companies' own count).
- Section 2's five subsections (Registered Companies, Registered Students, Company Applications,
  Ongoing Drives, Student Applications) are each collapsible/expandable, independent of one another —
  Section 1 (welcome, totals, search) is not collapsible.
- Both modals (Drive details, Application details) include a "Go back" button that closes them, in
  addition to the existing close (×) control.
- The Application modal shows the applying Student's photo and a "View Resume" download action; the
  Drive modal shows the Drive's location and the owning Company's logo. Since no upload flow exists in
  this milestone (Company/Student self-service dashboards are Milestones 4/5), these are demonstrated
  with seeded placeholder files rather than real uploaded content — the fields and rendering exist now
  so a later milestone's upload feature has somewhere to write to.
- "Company Applications" only ever shows pending Companies; there is no dashboard view of rejected
  Companies in this milestone. A rejection is effectively final from the UI's point of view (see Edge
  Cases) — reconsidering one is a direct-database action, out of scope here.
- Registered Students has no approval concept (Students self-register and are immediately usable, per
  Milestone 2) — its only per-row action is the same blacklist/whitelist toggle Registered Companies
  has.
- "Serial Number" in Ongoing Drives and Student Applications is a display-only row position, not a
  stored field — it's whatever order the list comes back in, numbered from 1.
- Since Milestone 4 (Company's own dashboard, where Drives are actually created) doesn't exist yet,
  this milestone's verification seeds at least one Drive directly (e.g. via `flask shell`) to
  demonstrate Ongoing Drives and Mark as Complete — the same approach already used for the previous
  design's Job Posting verification.
- No new Company/Student self-service actions are in scope here — this milestone is entirely
  Admin-facing. Company's and Student's own dashboards are Milestones 4 and 5.
