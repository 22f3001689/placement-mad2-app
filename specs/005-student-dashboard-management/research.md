# Phase 0 Research: Student Dashboard & Job Application System

No open `[NEEDS CLARIFICATION]` markers were left in the spec — the decisions below resolve every
technical unknown the Technical Context flagged.

## Decision: Real file upload, reusing Milestone 3's static directories

- **Decision**: `POST /api/student/profile` accepts `multipart/form-data` with text fields plus
  optional `photo`/`resume` files. Files are saved via `werkzeug.utils.secure_filename` under the
  same `app/static/uploads/photos/`/`app/static/uploads/resumes/` directories Milestone 3 already
  created for seeded placeholder files, named `<user_id>_<secure_filename>` to avoid collisions
  across Students.
- **Rationale**: Every `photo_path`/`resume_path` write before this milestone was seed-only; this is
  the first real upload path. Reusing the same directories and the `static_url()` helper
  (`app/utils.py`, Milestone 4) means Admin/Company's existing views need zero changes to start
  showing a Student's real uploaded files instead of seeded ones.
- **Alternatives considered**: A dedicated upload service/CDN — rejected outright, contradicts the
  constitution's Local-Demo-First principle; storing file bytes in the database (BLOB column) —
  rejected as unnecessary complexity when local filesystem storage already works for every other
  file this app serves.

## Decision: Extend two existing Company endpoints, don't add new ones

- **Decision**: `POST /api/company/applications/<id>/decision` gains an optional `remark` field in
  its request body (alongside the existing `status`); `POST /api/company/applications/<id>/interview`
  gains an optional `mode` field (alongside the existing `interview_datetime`).
- **Rationale**: Both are naturally part of the same action Company already performs (deciding a
  status, scheduling an interview) — a Company setting a remark without also touching status, or a
  mode without a time, isn't a scenario either source document describes. One endpoint per action
  stays true to Milestone 4's own research.md reasoning.
- **Alternatives considered**: Two new endpoints (`.../remark`, `.../interview-mode`) — rejected as
  splitting one logical action into two round-trips.

## Decision: Placement confirmation is plain text, not a generated PDF

- **Decision**: `GET /api/student/placement/confirmation` returns a `text/plain` response with
  `Content-Disposition: attachment`, containing the Placement's position, company, salary, and
  joining date in a simple formatted layout.
- **Rationale**: Neither source document specifies a format. Adding a PDF-generation library
  (`reportlab`, `weasyprint`, etc.) for one document type in a class project is exactly the kind of
  unrequested complexity the constitution's Principle VII warns against — a plain-text download
  still satisfies "download... placement confirmations" literally.
- **Alternatives considered**: Minimal HTML response with the same disposition — considered
  equally valid and simpler than PDF, but plain text needs even less markup for the same content;
  either would work, plain text was chosen as the smaller artifact.

## Decision: Drive detail viewing has no status restriction; only Apply does

- **Decision**: `GET /api/student/drives/<id>` returns a Drive's detail regardless of its
  `ongoing`/`completed` status. Only `POST /api/student/drives/<id>/apply` checks `status ==
  "ongoing"`.
- **Rationale**: The wireframe's dashboard "Applied Drives" table has its own "view details" button,
  which must keep working even after a Drive the Student already applied to later closes — Milestone
  1's own principle of retaining full history would be undermined if viewing a completed Drive's
  detail suddenly 404'd. Restricting only the state-changing action (Apply) matches spec.md's FR-006
  precisely, without inventing a view-time restriction the spec never asked for.
- **Alternatives considered**: Restricting viewing to `ongoing` Drives only, with a separate
  "history detail" path for closed ones — rejected as two code paths for what's really one read.

## Decision: Search covers only `ongoing` Drives, hardcoded server-side

- **Decision**: `GET /api/student/drives` (used for both Search and a Company's Current Drives)
  always filters to `status == "ongoing"` — this isn't a client-supplied `status` query param the
  way Milestone 3's Admin/Milestone 4's Company listings have one.
- **Rationale**: Per spec.md's Assumptions, a Student has no reason to search or browse `completed`
  Drives — they can't apply to them anyway, and Organizations' "Current Drives" is explicitly scoped
  to ongoing ones by User Story 2. Exposing a `status` param a Student could set to `completed` would
  just be unused surface area.
- **Alternatives considered**: Mirroring Admin/Company's optional `status` param for consistency —
  rejected; consistency isn't a goal in itself, and this endpoint's one real use never needs it.

## Decision: Filter/sort on the Applicants list instead of automatic eligibility rejection

- **Decision**: `GET /api/company/drives/<id>/applications` (Milestone 4) gains optional `status`
  (filter) and `sort=status` (group) query params. `GET /api/student/drives/<id>` gains
  `eligibility_criteria` in its response.
- **Rationale**: A direct follow-up to the constitution v1.2.0 amendment — dropping automatic
  rejection doesn't mean doing nothing about it. These two changes are what actually address "make
  shortlisting easier" without the fragility of parsing freeform eligibility text: the Student reads
  the criteria and self-selects before applying, and the Company can filter straight to `applied`
  (skip ones already decided) or group by status, both server-side query changes on data that
  already exists — no new table, no new endpoint.
- **Alternatives considered**: Building real eligibility parsing/matching against the freeform text
  — explicitly deferred, not rejected outright; revisit if a concrete need shows up (per spec.md's
  Assumptions, "a reasonable candidate once there's a concrete need for it").
