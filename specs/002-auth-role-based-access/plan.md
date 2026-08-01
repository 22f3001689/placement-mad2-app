# Implementation Plan: Authentication & Role-Based Access

**Branch**: `docs/milestone-2-plan` | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-auth-role-based-access/spec.md`

## Summary

Build a JSON auth API (register-student, register-company, login, logout, whoami) on top of
Milestone 1's `User`/`Company`/`Student` models, using Flask-Login session cookies (already wired
into the `User` model in Milestone 1). This is also the milestone where the Vue frontend is born: a
minimal Vite+Vue3 app with a router, a tiny auth state module, and one placeholder landing view per
role, served by Flask through a single Jinja entry-point shell per the constitution.

## Technical Context

**Language/Version**: Python 3.11 (backend, unchanged from Milestone 1); Node 20 LTS + npm (frontend
build tooling only — Node never runs in the served application, only at `npm run build` time)

**Primary Dependencies**:
- Backend: Flask, Flask-Login (session cookies — already added to `User` in Milestone 1), Flask-
  SQLAlchemy, Flask-Migrate (all existing, no new backend dependency added).
- Frontend: Vue 3, Vue Router. No Pinia and no axios — the auth state is one small object (current
  user), handled with a plain reactive JS module; HTTP calls use the browser's built-in `fetch`. Both
  would be reasonable choices on a bigger app, but neither pulls its weight for this milestone's
  actual scope (Principle VII).

**Storage**: SQLite, unchanged from Milestone 1.

**Testing**: No automated test suite — same decision and rationale as Milestone 1
(`../001-database-models-schema/research.md`); verified manually via `quickstart.md`.

**Target Platform**: Local developer machine. Two run modes: (a) dev — `npm run dev` (Vite dev
server on :5173, proxying `/api/*` to Flask on :5000) alongside `flask run`; (b) demo — `npm run
build` outputs into `app/static/dist/`, and Flask alone serves everything on one port. Both modes are
same-origin from the browser's point of view, so no CORS configuration is needed anywhere.

**Project Type**: Web application — first milestone where the frontend half actually exists.

**Performance Goals**: N/A — no load targets stated for this milestone.

**Constraints**: Bootstrap only for styling (via CDN link in the Jinja shell, no Sass build
pipeline); Jinja used only for that one shell template, never for a UI view (constitution Principle
I).

**Scale/Scope**: 5 API endpoints, 1 Jinja shell template, ~6 Vue views (Login, Register-Student,
Register-Company, and 3 placeholder role landing pages), 1 router, 1 auth state module.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Mandated Stack | Flask + Vue + Bootstrap (CDN) + SQLite unchanged; Jinja used only as the one entry shell, never for a UI view | PASS |
| II. Programmatic DB Creation | No schema changes this milestone — reuses Milestone 1's models/migrations as-is | PASS |
| III. Role-Based Access | Every endpoint's role check runs server-side (FR-010); single `User.role` column, no parallel login system | PASS |
| IV. Reuse Before Rebuild | Session mechanism (Flask-Login, login_user/logout_user/login_required), the login/register control flow, and the role-based post-login redirect all follow `../hms-app-main/app/routes/auth.py` almost line for line, adapted from HTML-form+redirect to JSON responses | PASS |
| V. Local-Demo-First | No CORS needed in either run mode; both are fully local, no cloud dependency added | PASS |
| VI. Milestone-Sliced | This plan covers Milestone 2 only — dashboards' real content stays out of scope (Milestones 3-5) | PASS |
| VII. Simple/Human/Surgical | Deliberately skips Pinia and axios (see Primary Dependencies); one small new abstraction (`role_required` decorator) is justified below, not because it's used more than once *today* but because every remaining core milestone (3-8) needs the identical check | PASS |

**Complexity justified**: adding a `role_required(*roles)` decorator (`app/decorators.py`) instead of
inline `if current_user.role not in (...): abort(403)` checks copied into every route, which is what
`../hms-app-main` does. `../hms-app-main` only ever has 3 roles across ~15 routes total and never
factored this out; this project's own Milestones 3-8 add dashboard/report/job endpoints for all three
roles, where the same check would otherwise be copy-pasted dozens of times. One four-line decorator is
a smaller, more honest artifact than that repetition — not a speculative abstraction, since the need
is already visible in the milestone list, not hypothetical.

## Project Structure

### Documentation (this feature)

```text
specs/002-auth-role-based-access/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── contracts/
│   └── auth-api.md       # Phase 1 output - the 5 endpoints
└── quickstart.md         # Phase 1 output
```

No `data-model.md`: this milestone adds no new entities (spec.md's Key Entities section is empty by
design — it's all behavior on Milestone 1's existing `User`/`Company`/`Student`).

### Source Code (repository root)

```text
app/
├── __init__.py            # + registers auth_bp; + one catch-all route serving the Jinja shell
├── models.py               # unchanged
├── decorators.py            # NEW: role_required(*roles) - wraps login_required + role check
├── routes/
│   └── auth.py               # NEW: auth_bp - register/student, register/company, login, logout, me
└── templates/
    └── index.html             # NEW: the one Jinja shell (script/link tags to the built Vue bundle)

frontend/                    # NEW: Vite + Vue 3 project
├── index.html                # Vite's own dev entry (unused in the "demo" run mode)
├── vite.config.js             # dev proxy /api -> http://localhost:5000; build.outDir ../app/static/dist
├── package.json
└── src/
    ├── main.js
    ├── App.vue
    ├── router/index.js         # /login, /register/student, /register/company, /admin, /company, /student
    ├── api/http.js               # thin fetch wrapper, always sends credentials: 'include'
    ├── state/auth.js             # reactive({ user: null }) + login()/logout()/fetchMe() helpers
    └── views/
        ├── Login.vue
        ├── RegisterStudent.vue
        ├── RegisterCompany.vue
        ├── AdminHome.vue           # placeholder - real content is Milestone 3
        ├── CompanyHome.vue         # placeholder - real content is Milestone 4
        └── StudentHome.vue         # placeholder - real content is Milestone 5
```

**Structure Decision**: `app/` keeps owning the repo root as the Flask API (per Milestone 1), and
`frontend/` is added as its own top-level Vite+Vue project, exactly as anticipated in Milestone 1's
plan.md. Vite builds straight into `app/static/dist/` so Flask's existing static-file serving covers
the built JS/CSS with zero new routes; only the one Jinja shell template and one catch-all route are
new on the Flask side for this milestone's frontend hookup.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| New `role_required` decorator not present in `../hms-app-main` | Every core milestone from here on (3-8) needs the same per-role check on multiple new endpoints | Copy-pasting the inline `if current_user.role not in (...): abort(403)` check (the reference project's approach) turns into real duplication once Milestones 3-8 add their endpoints — the decorator is the smaller artifact, not the more complex one |
