# Implementation Plan: Company Dashboard & Job/Application Management

**Branch**: `docs/milestone-4-plan` | **Date**: 2026-08-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/004-company-dashboard-management/spec.md`

## Summary

Add a JSON API under `/api/company` (create/list/complete Drives, list a Drive's Applications, view
one Application's detail, set its status, set its interview date/time), gated by a new
`company_approved_required` decorator (role check + approval check, already anticipated in Milestone
2's auth contract). On the frontend, replace the `CompanyHome.vue` placeholder with a single-page
dashboard mirroring Milestone 3's Admin dashboard pattern: Upcoming/Closed Drives tables, a Create
Drive modal, and a Drive's-Applications modal that swaps to an Application-detail modal on "review
application."

## Technical Context

**Language/Version**: Python 3.11 (backend, unchanged); Node 20 LTS + npm (frontend build tooling
only, unchanged).

**Primary Dependencies**: Flask, Flask-Login, Flask-SQLAlchemy, Flask-Migrate (all existing). Frontend:
Vue 3 (existing), reusing `Modal.vue` and `CollapsibleSection.vue` from Milestone 3 — no new
dependency.

**Storage**: SQLite. Real schema change this milestone (flagged in spec.md for review): `JobPosition`
gains `drive_name` and `eligibility_criteria`, loses `eligible_branches`/`min_cgpa`/
`eligible_graduation_year`; `Application` gains `interview_datetime`. One migration.

**Testing**: No automated test suite — same decision as Milestones 1-3; verified manually via
`quickstart.md`.

**Target Platform**: Local developer machine, same two run modes as before.

**Project Type**: Web application (unchanged).

**Performance Goals**: N/A.

**Constraints**: Bootstrap CSS only, no JS bundle (unchanged from Milestone 3); Jinja stays a single
entry shell.

**Scale/Scope**: 7 API endpoints under `/api/company`, 1 new decorator, 1 single-page Vue view
replacing the Milestone 2 `CompanyHome.vue` placeholder, 2 modals (Create Drive, Applications/
Application-detail — the latter swaps content rather than stacking two dialogs).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Mandated Stack | Flask + Vue + Bootstrap (CDN, CSS only) + SQLite unchanged; no new dependency | PASS |
| II. Programmatic DB Creation | Real column changes this milestone, but done via Flask-Migrate autogenerate + review, never manual SQL | PASS |
| III. Role-Based Access | Every endpoint wrapped in `company_approved_required` (built on the existing `role_required`) | PASS |
| IV. Reuse Before Rebuild | Drive ongoing/completed lifecycle, `Modal.vue`/`CollapsibleSection.vue`, and the approval-gate pattern all reused directly from Milestones 2-3 | PASS |
| V. Local-Demo-First | No new external service, no CORS change | PASS |
| VI. Milestone-Sliced | This plan covers Milestone 4 only — Student's own apply/view flow is Milestone 5; interview *reminders* (not scheduling itself) are Milestone 7 | PASS |
| VII. Simple/Human/Surgical | One decorator (not a duplicated inline check), one endpoint per action (no batch-save endpoint — see research.md), dropping unused columns instead of leaving dead speculative fields | PASS |

**Complexity justified**: `company_approved_required` is a new decorator, not a reuse of
`role_required` alone — justified because it's the exact check Milestone 2's own auth contract already
anticipated ("Active Company session, but the endpoint requires `approval_status == 'approved'`... →
`403` with `{"error": "Company is not yet approved"}`") and every endpoint in this milestone needs it;
writing the same two-line check inline seven times would be the actual duplication.

## Project Structure

### Documentation (this feature)

```text
specs/004-company-dashboard-management/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output - the schema change
├── contracts/
│   └── company-api.md      # Phase 1 output - the 7 endpoints
└── quickstart.md         # Phase 1 output
```

### Source Code (repository root)

```text
app/
├── models.py                  # JobPosition: +drive_name, +eligibility_criteria,
│                                 -eligible_branches, -min_cgpa, -eligible_graduation_year
│                               # Application: +interview_datetime
├── decorators.py                # + company_approved_required
├── routes/
│   └── company.py                 # 7 endpoints (see contracts/company-api.md)
data-seeds/
└── seed_data.py                     # sample JobPosition updated to the new fields
migrations/versions/
└── <new>_drive_fields_and_interview_datetime.py
frontend/src/
└── views/
    └── CompanyHome.vue                # REPLACES the Milestone 2 ping placeholder with the
                                        # single-page dashboard described in Summary
```

**Structure Decision**: Mirrors Milestone 3's Admin dashboard structure exactly — one view file, no
new router entries, reusing the same shared `Modal.vue`/`CollapsibleSection.vue` components rather than
introducing Company-specific equivalents.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| New `company_approved_required` decorator | Every one of this milestone's 7 endpoints needs both the role check and the approval check together | Inlining `if current_user.role != "company" or current_user.company_profile.approval_status != "approved": ...` in every route is the real duplication; Milestone 2's own contract already named this exact check |
