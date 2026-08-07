<!--
Sync Impact Report
Version change: 1.0.0 → 1.1.0
Modified principles: n/a
Added sections: Core Principles VII (Simple, Human, Surgical Code)
Removed sections: none
Templates requiring review: .specify/templates/plan-template.md (✅ no conflicts),
  .specify/templates/spec-template.md (✅ compatible), .specify/templates/tasks-template.md (✅ compatible)
Follow-up TODOs: none
-->

# Placement Portal Application (PPA) V2 Constitution

## Core Principles

### I. Mandated Technology Stack (NON-NEGOTIABLE)
The project MUST be built exclusively on: Flask (API backend), VueJS (UI — Vue CLI/advanced
tooling permitted but not required), Bootstrap (all HTML styling — no other CSS framework),
SQLite (the only database), Redis (caching), and Redis+Celery (background/scheduled/batch jobs).
Jinja2 templates MAY be used only as a single entry-point HTML shell that bootstraps the Vue
app — never to render actual UI views. No other framework, library, or database substitution is
permitted, including alternatives that are objectively "better" — this is fixed, graded coursework
and deviating risks the grading rubric. Any exception requires explicit user sign-off before a
spec or plan is written against it.

### II. Programmatic Database Creation
The database schema MUST be created entirely through code (SQLAlchemy models and/or Flask-
Migrate migrations). Manual schema creation via GUI tools (e.g. DB Browser for SQLite) is
forbidden. The single Admin user MUST be pre-created programmatically via a seed script — there
is no admin self-registration flow, and the system MUST support only one Admin account.

### III. Role-Based Access, Single Source of Truth
Exactly three roles exist — Admin, Company, Student — modeled via one unified `User` model with a
role discriminator (reusing the pattern already proven in the sibling reference project
`../hms-app-main`). Student accounts self-register directly; Company accounts self-register but
remain inactive/unapproved until the Admin approves them, gaining dashboard and drive-creation
access only after approval. Every API endpoint MUST enforce role and ownership checks
server-side — hiding an action in the Vue UI is never sufficient authorization.

### IV. Reuse Before Rebuild
Where the sibling reference project `../hms-app-main` (same author, same course, same core stack:
Flask, Flask-Login, SQLAlchemy, Flask-Migrate) already solves an equivalent backend problem —
auth/session patterns, `config.py` layout, Makefile targets, migrations setup, unified user-role
modeling — that pattern MUST be adapted and reused rather than reinvented. The one deliberate
divergence: Jinja-rendered server templates are replaced by a Vue SPA consuming JSON APIs, per
Principle I.

### V. Local-Demo-First
The entire application MUST run and be demoable on a local developer machine with no mandatory
cloud dependency (Redis/Celery run locally; any outbound notification channel — email, SMS, Google
Chat webhook — MUST degrade gracefully or be mockable for a local demo). Every feature must be
independently verifiable via a local run before being considered complete.

### VI. Spec-Driven, Milestone-Sliced Delivery
Work is sliced by the official Milestones document (Milestone 0 through the 8 core milestones,
followed by 2 recommended/optional milestones). Each milestone gets its own spec under `specs/`
and MUST be reviewed and accepted by the user before implementation begins on that milestone. Core
milestones may be implemented in any order; the recommended/optional milestones (UI/UX + PWA,
Reports/Charts/ATS) are out of scope until all core milestones are accepted. Each completed
milestone MUST be committed to git with a unique, milestone-specific commit message and pushed —
no milestone is "done" without that commit.

### VII. Simple, Human, Surgical Code
This is a student coursework project, not a production platform — code MUST read like it was
written by one focused person, not generated boilerplate. Concretely:
- Write the minimum code that satisfies the current milestone's requirements. No speculative
  configurability, no abstractions for something used once, no error handling for scenarios that
  cannot occur given the mandated stack and single-admin/local-demo constraints.
- Comments are written like a human explaining a non-obvious decision, not restating what the
  code already says. Prefer no comment over an obvious one.
- Changes to existing files touch only what the current task requires — no drive-by refactors,
  reformatting, or "improvements" to unrelated code. If dead code is noticed, flag it, don't
  silently delete it (unless the task is explicitly to remove it).
- Before implementing a non-trivial piece, state the plan and assumptions; if a simpler approach
  exists than what was asked for, say so rather than silently building the more complex thing.
- Every non-trivial task should have a stated, checkable definition of done (e.g. "this endpoint
  rejects a duplicate application with a 409" is verifiable; "handle applications properly" is not).

## Data & Access Constraints

- No database engine other than SQLite; no ORM/driver that requires a different engine.
- No CSS framework or component library other than Bootstrap.
- Caching MUST be applied to hot read endpoints (e.g. job/drive listings, company search, student
  search) via Redis, with explicit cache expiry/invalidation — stale reads after a write are a bug.
- A Student MUST NOT be able to submit more than one Application to the same Job Position/Drive.
- Applications MUST be rejected server-side if the Student fails the drive's eligibility criteria
  (branch, CGPA, year, etc.) at submission time.
- Complete history MUST be retained and queryable: a Student's full Application and Placement
  history persists even after a drive closes or a job is filled.
- Companies can create/manage Job Positions and view/act on Applications only while their company
  profile is in the Admin-approved state; Admin can revoke approval (blacklist/deactivate) at any
  time, which MUST immediately cut off that capability.

## Delivery Workflow

- Every milestone starts as a spec (`/speckit-specify`) reviewed by the user, then a plan
  (`/speckit-plan`), before any implementation code is written.
- Specs and plans MUST name the exact mandated-stack component used for each capability (e.g.
  "cached via Redis with 60s TTL", "job scheduled via Celery Beat") — vague language like "add
  caching" without the concrete mechanism is not acceptable at plan time.
- Where a spec's design intentionally departs from a directly-reusable `../hms-app-main` pattern,
  the spec MUST state why.
- Database schema changes ship as Flask-Migrate migrations, never hand-edited `.db` files.

## Governance

This constitution supersedes ad-hoc technical choices made in specs, plans, or during
implementation. Any proposed deviation from Principle I (Mandated Technology Stack) MUST be
raised with and approved by the user before it is written into a spec or plan — it is not a
judgment call the assistant makes unilaterally, because it risks the grading rubric. Amendments to
this constitution require: a stated rationale, an explicit version bump (MAJOR for
removing/redefining a principle, MINOR for adding one, PATCH for wording/clarity), and an updated
Sync Impact Report at the top of this file. All specs and plans should be checked against this
constitution before implementation begins.

**Version**: 1.1.0 | **Ratified**: 2026-08-01 | **Last Amended**: 2026-08-01
