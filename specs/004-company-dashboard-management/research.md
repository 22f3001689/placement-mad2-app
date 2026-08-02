# Phase 0 Research: Company Dashboard & Job/Application Management

No open `[NEEDS CLARIFICATION]` markers were left in the spec — the decisions below resolve every
technical unknown the Technical Context flagged.

## Decision: A new `company_approved_required` decorator, composing `role_required`

- **Decision**: `app/decorators.py` gains `company_approved_required(view)`, which wraps
  `role_required("company")` and additionally checks
  `current_user.company_profile.approval_status == "approved"`, returning
  `{"error": "Company is not yet approved"}`, `403` if not.
- **Rationale**: Milestone 2's own auth contract (`specs/002-auth-role-based-access/contracts/auth-api.md`)
  already documented this exact response shape as the general pattern for "every endpoint added from
  Milestone 3 onward" that needs it — this milestone is the first to actually need it, so building it
  now (not earlier, speculatively) matches the constitution's simplicity principle.
- **Alternatives considered**: Inlining the approval check in every one of the 7 new routes — rejected
  as the real duplication, exactly the reasoning `role_required` itself was built on in Milestone 2.

## Decision: Every action commits immediately — no batch "save" endpoint

- **Decision**: Setting an Application's status or interview date/time each POST immediately and take
  effect right away. There is no endpoint that saves multiple pending changes at once.
- **Rationale**: The wireframe's "Update Applications for the Drive" screen has a page-level "Save"
  button alongside per-row "review application" buttons, which could suggest batching, but the
  "Student Application" detail screen it opens has no Save button of its own — only a status dropdown
  and Back. Given the rest of this app (Milestones 2-3) always commits immediately on action, and
  batching risks losing an Admin's/Company's edits if they navigate away before an explicit save,
  immediate-commit is both simpler and safer. The spec's own wording ("saved... shown correctly the
  next time viewed") doesn't require batching either.
- **Alternatives considered**: A page-level batch save matching the wireframe literally — rejected;
  it would need client-side pending-edit tracking and a bulk-update endpoint for a benefit (fewer
  network calls) this app has never needed at its current scale.

## Decision: Drop `JobPosition`'s three structured eligibility columns

- **Decision**: Remove `eligible_branches`, `min_cgpa`, `eligible_graduation_year`; add one freeform
  `eligibility_criteria` text column instead.
- **Rationale**: These three columns were added in Milestone 1 before any real Create-Drive UI existed.
  The actual wireframe has one freeform Eligibility Criteria text box. Nothing in the codebase has ever
  queried the three structured columns for filtering, and Milestone 5's own spec (student search: "by
  company, position, or required skills") doesn't ask for eligibility filtering either. Keeping three
  unused, never-wired-up columns is exactly the speculative complexity the constitution's Karpathy
  guidelines principle warns against.
- **Alternatives considered**: Keeping all three structured columns *and* adding the new freeform one
  — rejected; two ways to express the same concept where only one is ever written to or read is worse
  than one, not safer. Flagged explicitly in spec.md for a final human decision before this lands,
  since dropping columns is harder to reverse than adding them.

## Decision: `drive_name` is a new field, separate from the existing `title`

- **Decision**: `JobPosition.title` keeps meaning "Job Title" (e.g. "Data Scientist"); a new
  `drive_name` column holds the wireframe's separate "Drive Name" (e.g. "Drive 3").
- **Rationale**: The wireframe's Create Drive form and dashboard tables treat these as two distinct,
  independently meaningful labels — a Company might run multiple Drives for the same Job Title across
  different cohorts/colleges, each needing its own Drive Name.
- **Alternatives considered**: Reusing `title` for both, showing it in both places — rejected; it
  would silently lose the distinction the wireframe explicitly draws.

## Decision: Interview scheduling is one `interview_datetime` column, no separate entity

- **Decision**: `Application` gains one nullable `interview_datetime` column, settable independently of
  status.
- **Rationale**: Per direct clarification, this is a minimal field for Milestone 7's future reminder
  job to read — not a full interview-slots/calendar system, which nothing in either source document
  asks for.
- **Alternatives considered**: A separate `Interview` entity (supporting multiple rounds, interviewer
  assignment, etc.) — rejected as speculative for a milestone whose own wireframe shows no such detail.

## Decision: One modal at a time, swapping content instead of stacking dialogs

- **Decision**: The Applications-for-a-Drive list and the single-Application detail are two separate
  modal states in `CompanyHome.vue`, but only one is ever shown at once — opening "review application"
  closes the Applications-list modal and opens the detail modal; "Back" reverses that.
- **Rationale**: `Modal.vue` (Milestone 3) is a simple single-dialog component; stacking two would need
  z-index/backdrop handling it doesn't have. Swapping which one is visible is simpler and matches the
  wireframe's own screen-to-screen navigation (Back returns to the list, it doesn't overlay on top of
  it).
- **Alternatives considered**: Extending `Modal.vue` to support stacking — rejected as unnecessary
  complexity for a two-screen drill-down that swapping content handles just as well.
