# Feature Specification: Authentication & Role-Based Access

**Feature Branch**: `002-auth-role-based-access`

**Created**: 2026-08-01

**Status**: Draft

**Input**: Milestone 2 (per official Milestones doc) — "Authentication and Role-Based Access
(Admin/Company/Student)". Students self-register and log in. Companies register and log in, gaining
company-only capabilities only once Admin-approved. Admin has a predefined login only, with no
registration path. Every logged-in user is routed to a role-appropriate area, and every role-specific
action is checked server-side.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A Student signs up and logs in on their own (Priority: P1)

A prospective Student creates their own account and logs in, with no help from anyone else, and lands
somewhere clearly meant for Students.

**Why this priority**: Students are the largest user group and the most self-service — nothing about
their path depends on Admin or Company workflows, making this the cleanest, most independent slice to
deliver and demo first.

**Independent Test**: With no other accounts touched, register a brand-new Student account and log in
with it; confirm the session recognizes them as a Student.

**Acceptance Scenarios**:

1. **Given** no account exists for a given username, **When** someone registers as a Student with a
   password, **Then** an account is created and they can immediately log in with those credentials.
2. **Given** a username that's already taken, **When** someone tries to register with it, **Then**
   registration is rejected with a clear "already taken" message and no account is created or changed.
3. **Given** a logged-in Student, **When** they log out, **Then** their session ends and any further
   request to a Student-only area requires logging in again.

---

### User Story 2 - Admin can only ever be the one pre-existing account (Priority: P1)

The Admin logs in with the account that was already set up when the system was first deployed —
there is no page, form, or endpoint anywhere that lets anyone create an Admin account.

**Why this priority**: Every approval workflow (Company approval, drive approval) depends on Admin
access existing and staying singular; if this is wrong, it undermines the trust model of the whole
application.

**Independent Test**: Attempt to register a new account with an Admin role through every registration
path exposed by the system and confirm all of them refuse it; then log in with the pre-existing Admin
account and confirm it works.

**Acceptance Scenarios**:

1. **Given** the pre-existing Admin account from setup, **When** the Admin logs in with the correct
   username and password, **Then** they land somewhere clearly meant for Admins.
2. **Given** any registration entry point in the system, **When** an attempt is made to create a
   second Admin account through it (whether by picking "Admin" in a form or manipulating a request
   directly), **Then** the attempt is refused and no such account is created.

---

### User Story 3 - A Company signs up, logs in, and sees its real approval state (Priority: P1)

A Company registers its own account and logs in immediately afterward, seeing plainly whether it's
still waiting for Admin approval, and it can't use any company-only capability until that approval
happens.

**Why this priority**: Companies are the second core actor and their approval gate is central to the
whole platform's trust model (only vetted companies can post drives) — this needs to work before any
company-facing dashboard work (Milestone 4) can build on it.

**Independent Test**: Register a new Company account, log in with it while still unapproved, and
confirm the session shows "pending" and blocks any company-only action; then have an Admin approve it
and confirm the same account can now use that capability.

**Acceptance Scenarios**:

1. **Given** no account exists for a given username, **When** someone registers as a Company with a
   password, **Then** an account is created with its approval left in a pending state, and they can
   log in immediately.
2. **Given** a Company account that hasn't been approved yet, **When** it logs in, **Then** the
   session clearly reflects the pending state, and any attempt to use a company-only capability (such
   as posting a Job Position) is refused.
3. **Given** a Company account that has since been approved by Admin, **When** it logs in, **Then**
   the session reflects the approved state and company-only capabilities are available.

---

### User Story 4 - Nobody can reach another role's area, even by trying directly (Priority: P2)

Every request for a role-specific page or action is checked on the server, not just hidden in the
interface — a Student can't perform a Company or Admin action, a Company can't perform an Admin
action, and an unauthenticated or expired session gets sent back to log in instead of seeing anything
protected.

**Why this priority**: This is what makes the role split in User Stories 1–3 actually mean something.
It matters most once real dashboards exist (Milestones 3–5), but the check has to be built now so
nothing downstream can accidentally skip it.

**Independent Test**: While logged in as a Student, directly attempt a Company-only and an Admin-only
action and confirm both are refused; then log out and attempt to reach a role-specific area and
confirm it requires logging in first.

**Acceptance Scenarios**:

1. **Given** a logged-in Student, **When** they attempt any Company-only or Admin-only action,
   **Then** it is refused, regardless of whether the interface would have hidden the option from them.
2. **Given** a logged-in Company, **When** it attempts any Admin-only action, **Then** it is refused.
3. **Given** no logged-in session (or an expired one), **When** a role-specific area is requested,
   **Then** the request is sent to log in rather than shown any protected content or a raw error.

---

### Edge Cases

- What happens when a deactivated/blacklisted account (Admin, Company, or Student) tries to log in
  with the correct password? Login must still be refused.
- What happens when someone submits the wrong password for a real username? The system must reject it
  with the same generic message used for a nonexistent username — no hint about which part was wrong.
- What happens to a Company's session if Admin rejects (rather than approves) its profile? It behaves
  the same as "pending" — company-only capabilities stay blocked; there's no separate "rejected"
  lockout beyond that in this milestone.
- What happens if someone already logged in as one role tries to register a second account? Registration
  doesn't depend on being logged out first, but it always creates an independent new account — it never
  changes the role of whoever is currently logged in.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let a new Student create their own account (self-registration) with a
  unique username and a password.
- **FR-002**: System MUST let a new Company create their own account (self-registration) with a
  unique username and a password, leaving its approval status pending until Admin acts on it.
- **FR-003**: System MUST NOT expose any path — form, page, or direct request — that creates an Admin
  account; the one Admin account is the one already seeded before this milestone.
- **FR-004**: System MUST let any active (non-deactivated) Admin, Company, or Student log in with
  their username and password, and keep them recognized as logged in across subsequent requests until
  they log out or their session/token expires.
- **FR-005**: System MUST refuse login for a deactivated/blacklisted account even when the password is
  correct.
- **FR-006**: System MUST refuse a login attempt with an incorrect username or password, showing the
  same generic message either way.
- **FR-007**: System MUST route a user to a role-appropriate landing area right after login — Admin,
  Company, or Student — even though the full content of that area is delivered in later milestones.
- **FR-008**: System MUST let a Company log in and see its own real approval state at any time,
  regardless of whether it is pending, approved, or rejected.
- **FR-009**: System MUST block every company-only capability for a Company account until Admin has
  approved it, independent of whether the Company is currently logged in.
- **FR-010**: System MUST check the caller's role on the server for every role-specific action or
  page — no role-specific capability may rely on the interface alone to hide it from other roles.
- **FR-011**: System MUST let a logged-in user log out, ending their session/token immediately so nothing
  more can be done with it.
- **FR-012**: System MUST send an unauthenticated or expired-session request for a protected area to
  the login flow rather than exposing an error page or any protected data.

### Key Entities

- No new entities beyond Milestone 1's `User`, `Company`, and `Student` — this milestone is entirely
  about the login/registration/session behavior around those existing records.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A brand-new Student can register and be logged in within a minute, with zero manual or
  Admin-side steps required.
- **SC-002**: A brand-new Company sees a clear pending-approval indicator immediately after their
  first login — before any Admin action has happened.
- **SC-003**: Every attempted cross-role action (Student attempting Company/Admin actions, Company
  attempting Admin actions) is blocked — not silently allowed — across a full pass of the role-check
  scenarios in User Story 4.
- **SC-004**: Across the whole system, the only way to log in as Admin is with the account seeded in
  Milestone 1 — no user-facing flow can create a second one.
- **SC-005**: A deactivated account's login attempt is rejected 100% of the time, even with the
  correct password.

## Assumptions

- Registration collects only what's needed to create the account and its minimal role identity
  (username, password, plus one identifying field — company name for a Company, full name for a
  Student). Richer profile detail (skills, resume, industry, location, etc.) is filled in later via
  the dashboards built in Milestones 4 and 5, not at registration time.
- "Predefined login only" for Admin (Milestone doc wording) means the Milestone 1 seeded account is
  the sole Admin; nothing in this milestone adds a way to create a second one, by any role.
- "Company: register + login only (approved by Admin)" (Milestone doc wording) is read together with
  Milestone 4's wording ("Companies can only access the dashboard when approved by admin") — a Company
  CAN log in immediately after registering, but company-only capabilities stay blocked until approved.
  This is not read as "cannot log in at all," since that would leave a pending Company with no way to
  even check its own status.
- No password-reset/forgot-password flow is in scope — neither source document mentions one.
- No third-party/social login is in scope — neither source document mentions one.
- How "staying logged in" is technically implemented (cookie-based session vs. bearer token) is a
  planning-level decision, not a business requirement, and doesn't change any requirement above.
