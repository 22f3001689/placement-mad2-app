# Feature Specification: Backend Jobs — Interview Reminders, Placement Reports, and Triggered Exports

**Feature Branch**: `007-backend-jobs`

**Created**: 2026-08-08

**Status**: Draft

**Input**: User description: "Milestone 7: Backend Jobs - Interview Reminders, Placement Reports, and Triggered Jobs (Celery + Redis). Setup Celery workers, Celery Beat, and Redis server. Interview Reminder Job: send reminders to students with scheduled interviews via real email (SMTP through a Mailtrap sandbox, credentials via a `.env` file, never committed), rendered from a stored, templated email body. Placement Report Job: generate periodic reports for companies with application statistics, placements, and analytics (HTML report, downloadable, PDF out of scope). User-triggered CSV Export: students and companies can request an asynchronous export of their own application/placement history; once the job completes, an email alert is delivered, and the completed file becomes available for download (poll-based)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Student gets reminded of an upcoming interview automatically (Priority: P1)

A Student has an interview scheduled on an Application. Without anyone manually checking, the system automatically notifies them ahead of time so they don't miss it.

**Why this priority**: This is the milestone's headline feature and the one with real user value — every other capability in this milestone (reports, exports) is administrative convenience, but a missed interview is a real harm to a Student. It's also the first proof that background/scheduled jobs work at all in this app (nothing today runs outside a request).

**Independent Test**: Schedule an interview for a time in the near future, wait for (or manually trigger) the periodic reminder job to run, and confirm a reminder email was delivered to that Student's registered email address (visible in the configured mail sandbox, or in the application log if no mail server is configured) referencing that Student and that interview's date/time.

**Acceptance Scenarios**:

1. **Given** an Application with an `interview_datetime` in the near future that hasn't been reminded yet, **When** the periodic reminder job runs, **Then** exactly one reminder email is delivered to that Student's registered email address, referencing the Student, the Company, and the interview date/time.
2. **Given** an Application already reminded once, **When** the periodic reminder job runs again before the interview happens, **Then** no duplicate reminder is sent for that same Application.
3. **Given** no mail server is configured, **When** a reminder would otherwise be sent, **Then** the rendered email content is written to the application log instead, and no error is raised.
4. **Given** an Application's interview has already passed, **When** the periodic reminder job runs, **Then** no reminder is sent for it.

---

### User Story 2 - Student or Company exports their own history as CSV without blocking the UI (Priority: P1)

A Student wants a CSV of their own application history; a Company wants a CSV of applications/placements across its drives. Requesting this doesn't freeze their screen — they keep using the app and come back to download the file once it's ready.

**Why this priority**: Directly requested ("User-triggered CSV Export") and, unlike the report job, is user-initiated and immediately verifiable — a natural second proof point that async jobs plus job-status polling work end-to-end.

**Independent Test**: As a Student (or Company), request an export, confirm the request returns immediately (not blocked on the export finishing), poll the job's status until it reports ready, then download a CSV containing that Student's own applications (or that Company's own applications/placements) with no other user's rows in it.

**Acceptance Scenarios**:

1. **Given** a Student requests an export of their own application history, **When** the request is made, **Then** the system responds immediately with a job reference and the export continues in the background.
2. **Given** an export job is in progress, **When** the requester checks its status, **Then** they see whether it is still running or ready for download — never another user's job.
3. **Given** an export job has completed, **When** the requester checks its status or downloads the file, **Then** the CSV contains only rows belonging to that requester (their own applications for a Student; their own drives'/applications' for a Company) and an email alert (per User Story 1's delivery mechanism) was sent to their registered address noting completion.
4. **Given** a Company requests an export, **When** the CSV is generated, **Then** it covers that Company's own applications and placements only, never another Company's.

---

### User Story 3 - Admin/Company get a periodic placement report without asking anyone to compile it (Priority: P2)

On a recurring schedule, a report summarizing application statistics and placement outcomes is generated automatically for each Company, without anyone needing to request it.

**Why this priority**: Valuable but lower urgency than Stories 1-2 — it's a convenience/analytics feature with no direct user action tied to a real-time expectation, and both prior stories already establish the scheduled-job and async-job plumbing this one reuses.

**Independent Test**: Manually trigger the periodic report job, then confirm a report file was generated for each Company with ongoing/completed drives, containing that Company's own application counts, status breakdown, and placement count/details for the covered period, downloadable the same way as an export.

**Acceptance Scenarios**:

1. **Given** a Company has drives with applications, **When** the periodic report job runs, **Then** a report is generated for that Company covering the period since the last report, showing total applications, a breakdown by status, and placements made in that period.
2. **Given** a Company has no drives or applications at all, **When** the periodic report job runs, **Then** no report is generated for that Company (nothing to report).
3. **Given** a report has been generated, **When** the Company views their reports, **Then** they can download it and it contains only their own data.

### Edge Cases

- If the mail server is unreachable or rejects the send, the reminder/alert must still be recorded in the application log so the failure is visible for debugging — a failed delivery must never crash the job or silently vanish.
- Mail credentials (host, port, username, password) MUST never be committed to source control — they are read from environment variables provided via a local, untracked `.env` file, with an example/template file (placeholder values only) committed instead.
- Existing Student/Company accounts created before email capture existed have no email on file; the migration that adds the column MUST handle this without breaking login for those accounts, and any job attempting to email such an account MUST skip it (logged as skipped) rather than fail.
- Re-running the periodic reminder or report job (e.g. after a restart) must not produce duplicate reminders for an Application already reminded, or duplicate reports for a period already reported.
- An export or report request must never surface another user's data, even under concurrent requests from different users at the same time.
- If Redis or the background worker is not running, a request to start an export must fail with a clear, immediate error rather than hanging indefinitely waiting for a job that will never run.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST run a recurring job that checks for Applications with an upcoming, not-yet-reminded interview and delivers exactly one reminder email per such Application to that Student's registered email address.
- **FR-002**: The system MUST capture a required, unique email address for every Student and Company at registration (Admin's is seeded), and MUST render every reminder/alert email from a stored, reusable template rather than hand-building message text inline per call site.
- **FR-002a**: The system MUST send email via a configured SMTP server, falling back to a local application log entry (containing the fully-rendered subject/body) when no SMTP server is configured, with no error surfaced to the end user in either case.
- **FR-002b**: SMTP credentials MUST be supplied via environment variables (loaded from a local, untracked `.env` file) and MUST NOT appear in any committed file.
- **FR-003**: The system MUST allow a Student to request an asynchronous export of their own application history, and a Company to request one of its own applications/placements, without blocking on completion.
- **FR-004**: The system MUST let the requester check the status of their own export/report job (pending, running, ready, or failed) and MUST NOT expose another user's job status or content.
- **FR-005**: The system MUST make a completed export or report available as a downloadable file once ready.
- **FR-006**: The system MUST run a recurring job that generates a placement/application statistics report per Company for the period since that Company's last report, skipping Companies with no data to report.
- **FR-007**: The system MUST NOT send a duplicate interview reminder for the same Application, or a duplicate report for a Company for a period already covered.
- **FR-008**: The system MUST continue to function for all previously-existing features if Redis/the background worker is not running — background jobs degrade (export/report requests fail clearly) without breaking the rest of the app.

### Key Entities

- **Reminder record**: Tracks that a given Application's interview has already been reminded, so the recurring job can skip it next run.
- **Export/Report Job**: Represents one asynchronous request (export or report), owned by exactly one User (Student or Company), with a status (pending/running/ready/failed) and, once ready, a downloadable file.
- **Email Template**: A named, reusable email body (with placeholders for the specific reminder/alert's details — e.g. student name, interview time, company name) plus its subject line, used to render every outgoing email consistently rather than duplicating message-building logic per notification type.
- **User email** (new attribute on the existing `User` entity): the address reminders/alerts are sent to; required going forward, captured at registration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Applications with an upcoming interview receive exactly one reminder before that interview time, with zero duplicates, across repeated job runs.
- **SC-002**: A Student or Company can request an export and continue using the app immediately — the request never blocks their session waiting for the export to finish.
- **SC-003**: Every downloaded export or report contains only the requesting Student's or Company's own data — verified with zero cross-user data leakage across repeated tests.
- **SC-004**: A Company with active drives receives a new placement report every reporting period with zero manual compilation effort; a Company with no activity receives none (no empty noise).

## Assumptions

- Reports are generated as downloadable HTML files, not PDF — PDF rendering is out of scope for this milestone (per user decision).
- Notifications are delivered as real email via SMTP (a sandbox mail-catcher service in local dev, a real provider in a real deployment), not a Chat webhook or SMS — a webhook can only post to one shared Space/channel and can't target an individual recipient, and SMS needs a paid provider; email is the only one of the three that both targets a specific person and has a zero-cost local fallback (per user decision).
- Every Student/Company registration now requires a valid-looking email address (this is a data-model change: a required, unique `email` column is added to `User`); Admin's is seeded. Existing pre-migration rows without one are backfilled or left null and simply skipped by any job that would email them (see Edge Cases).
- If no SMTP server is configured, the fully-rendered email (subject + body) is written to the application log instead of sent — this satisfies the constitution's "must degrade gracefully or be mockable for local demo" requirement without needing any external service by default.
- SMTP credentials live only in a local, untracked `.env` file (loaded by both the Flask app and the Celery worker process) — a committed `.env.example` documents the required variable names with placeholder values, never real credentials.
- Email Template rows are seeded (like `Branch`/`Skill`), not user-editable through any admin UI in this milestone — that's a reasonable future enhancement, not required by the milestone's stated scope.
- "Upcoming interview" for the reminder job means within a fixed lookahead window (not immediately at scheduling time) — the exact window is a technical/plan-level detail, not a product decision, and defaults to a reasonable value (e.g. reminding once per interview, checked periodically rather than at an exact minute).
- Export/report readiness is discovered by the requester polling a status endpoint from the frontend, not by a server-push mechanism (per user decision) — consistent with this app's existing no-websocket, request/response architecture.
- The recurring reminder and report jobs run on a fixed schedule managed by the job scheduler; no user-facing UI to change that schedule is in scope for this milestone.
