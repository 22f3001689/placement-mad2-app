# Implementation Plan: Student Dashboard & Job Application System

**Branch**: `docs/milestone-5-plan` | **Date**: 2026-08-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-student-dashboard-management/spec.md`

## Summary

Add a JSON API under `/api/student` (profile update with real file upload, browse
Organizations/Drives, search, apply, own Application history, placement confirmation download),
gated by the existing `role_required("student")`. Extend two of Milestone 4's existing
`/api/company` endpoints with two small new fields (`remark`, `interview_mode`) so Company can set
what this milestone's Student view reads. This is the first milestone with a real file-upload
endpoint — every `photo_path`/`resume_path` before now was seed-only.

## Technical Context

**Language/Version**: Python 3.11 (backend, unchanged); Node 20 LTS + npm (frontend build tooling
only, unchanged).

**Primary Dependencies**: Flask, Flask-Login, Flask-SQLAlchemy, Flask-Migrate (all existing).
Werkzeug's `secure_filename` for the new file-upload endpoint (already a transitive dependency of
Flask, no new package). Frontend: Vue 3 (existing), reusing `Modal.vue` — no new dependency.

**Storage**: SQLite. Real schema change: `Company` gains `overview`; `Application` gains
`interview_mode` and `company_remark` (see data-model.md). Uploaded files land under the same
`app/static/uploads/{photos,resumes}/` directories Milestone 3 already established for seeded ones.

**Testing**: No automated test suite — same decision as Milestones 1-4; verified manually via
`quickstart.md`.

**Target Platform**: Local developer machine, same two run modes as before.

**Project Type**: Web application (unchanged).

**Performance Goals**: N/A. Redis caching for hot read endpoints (job/drive listings, search) is a
constitution-level requirement but explicitly deferred to Milestone 8 ("API Performance
Optimization and Caching") by the Milestones doc's own slicing — not added here.

**Constraints**: Bootstrap CSS only, no JS bundle (unchanged); Jinja stays a single entry shell.
Eligibility is self-attested freeform text, not server-checked (constitution amended to v1.2.0
during this milestone's planning — see `.specify/memory/constitution.md`'s Sync Impact Report).

**Scale/Scope**: 9 new endpoints under `/api/student`, 2 endpoints under `/api/company` gaining an
optional field each, 1 new decorator-free file-upload code path, 1 single-page Vue view (`StudentHome.vue`)
replacing the Milestone 2 ping placeholder, reusing `Modal.vue` for Organization/Drive/History
detail popups.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Mandated Stack | Flask + Vue + Bootstrap (CDN, CSS only) + SQLite unchanged; no new dependency | PASS |
| II. Programmatic DB Creation | Schema change via Flask-Migrate autogenerate + review, never manual SQL | PASS |
| III. Role-Based Access | Every endpoint wrapped in the existing `role_required("student")`; every Application/Drive lookup scoped to the caller | PASS |
| IV. Reuse Before Rebuild | Reuses Milestone 3's static-upload directories/serving, Milestone 4's Drive ongoing/completed lifecycle and Application status vocabulary, `Modal.vue` | PASS |
| V. Local-Demo-First | No new external service; uploaded files stay local under `app/static/` | PASS |
| VI. Milestone-Sliced | This plan covers Milestone 5 only — Redis caching (Milestone 8) and any Company-side "finalize Placement" flow (unassigned, future) are explicitly not built here | PASS |
| VII. Simple/Human/Surgical | Extends 2 existing Company endpoints with one optional field each instead of adding new endpoints; placement confirmation is plain text, not a new PDF dependency | PASS |

**Constitution amendment during this plan** (v1.1.0 → v1.2.0): the Data & Access Constraints'
server-side eligibility-rejection requirement was replaced with a statement that eligibility is
freeform/self-attested, since Milestone 4 already dropped the structured columns it would have
needed, per direct user decision. See the constitution's own Sync Impact Report for the full
rationale — this is not a unilateral deviation, it was raised and approved before this plan was
written, per the Governance section.

No other complexity to justify.

## Project Structure

### Documentation (this feature)

```text
specs/005-student-dashboard-management/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output - Company.overview, Application.interview_mode/company_remark
├── contracts/
│   └── student-api.md      # Phase 1 output - the 9 new endpoints + the 2 extended Company ones
└── quickstart.md         # Phase 1 output
```

### Source Code (repository root)

```text
app/
├── models.py                  # Company: +overview
│                               # Application: +interview_mode, +company_remark
├── routes/
│   ├── student.py                 # 9 endpoints (see contracts/student-api.md)
│   └── company.py                  # decide_application: +remark; schedule_interview: +mode
data-seeds/
└── seed_data.py                     # sample Company.overview value
migrations/versions/
└── <new>_company_overview_and_application_feedback_fields.py
frontend/src/
└── views/
    └── StudentHome.vue                # REPLACES the Milestone 2 ping placeholder with the
                                        # single-page dashboard described in Summary
```

**Structure Decision**: Mirrors Milestones 3-4's dashboard structure exactly — one view file, no new
router entries, reusing `Modal.vue`. The one deviation from a pure "new milestone, new files" shape
is touching `app/routes/company.py` again, justified in Complexity Tracking below.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Modifying Milestone 4's `company.py` endpoints instead of leaving it untouched | `remark`/`interview_mode` are Company-set values this milestone's Student view needs to read; they belong on the same action (deciding status, scheduling an interview) Company already performs, not a new one | Adding two new Company endpoints (`.../remark`, `.../interview-mode`) alongside the existing two would split one logical action across two round-trips for no benefit — same reasoning Milestone 4 itself used to justify one decision endpoint over separate approve/reject routes |
