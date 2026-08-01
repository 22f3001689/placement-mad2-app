# Phase 0 Research: Admin Dashboard & Management

No open `[NEEDS CLARIFICATION]` markers were left in the spec — the decisions below resolve every
technical unknown the Technical Context flagged.

## Decision: Drives get no per-Drive Admin approval — only Company approval gates them

- **Decision**: Drop the original draft's `POST /api/admin/job-positions/<id>/decision` entirely.
  `JobPosition.status` becomes `"ongoing"` (default) / `"completed"` only, set via one new
  `POST /api/admin/job-positions/<id>/complete` endpoint.
- **Rationale**: Direct product clarification: Admin approving a Company is what unlocks that
  Company's ability to create Drives at all; once approved, the Company self-manages Drives end-to-end
  (create, accept Applications, mark complete). A second, per-Drive Admin gate would duplicate a
  decision Admin already made at the Company level.
- **Alternatives considered**: Keeping the original `pending`/`approved`/`rejected` Job Posting
  approval workflow from the first draft — rejected outright per the clarification; it modeled a
  two-layer approval (Company, then each of its Drives) that isn't how the product actually works.

## Decision: Single-page dashboard, not a router tree of sub-pages

- **Decision**: One `AdminHome.vue` view renders Section 1 (welcome + totals + search) and Section 2's
  five subsections inline. The four `/admin/companies`, `/admin/students`, `/admin/job-postings`,
  `/admin/applications` routes from the original draft are removed.
- **Rationale**: Directly matches the requested layout — one page, two sections, five subsections
  within the second. A router tree was reasonable for the original per-entity-page draft, but it's the
  wrong shape for what's actually being built now.
- **Alternatives considered**: Keeping the sub-pages and just changing what's on each — rejected,
  since the request is explicitly for one page, not four.

## Decision: One search bar, filtering two of the five subsections

- **Decision**: A single search input in Section 1 re-fetches both `GET /api/admin/companies?q=...`
  and `GET /api/admin/students?q=...` together, updating Registered Companies and Registered Students.
  It does not touch Company Applications, Ongoing Drives, or Student Applications.
- **Rationale**: Matches the requested Section 1 description exactly ("search Students or companies");
  the other three subsections are queues/oversight lists, not something the mockup describes as
  searchable.
- **Alternatives considered**: A per-subsection search box on every list — rejected as more UI than
  requested for a first pass; nothing in the request asks to search Drives or Applications.

## Decision: One toggle endpoint for blacklist/whitelist, reused across Companies and Students

- **Decision**: Keep the single `POST /api/admin/users/<id>/toggle-active` from the original draft,
  operating on `User.id`. The UI relabels it Blacklist/Whitelist (color-coded) instead of
  Deactivate/Reactivate — same endpoint, same `is_active` column, only the button copy/color changed.
- **Rationale**: This part of the original design already matched the request once relabeled; no
  reason to introduce two endpoints (deactivate/reactivate) where one toggle already works, and it
  still mirrors `../hms-app-main/app/routes/admin.py`'s blacklist-toggle pattern.
- **Alternatives considered**: N/A — this decision is unchanged from the original draft.

## Decision: Hand-rolled `Modal.vue`, no Bootstrap JS bundle

- **Decision**: A small shared component styled with Bootstrap's existing modal CSS classes
  (`.modal`, `.modal-dialog`, `.modal-content`), shown/hidden with a plain `v-if` bound to a prop —
  not Bootstrap's `data-bs-toggle`/JS bundle.
- **Rationale**: The constitution's Bootstrap principle is CSS/styling, not a mandate to load
  Bootstrap's JS; both modals needed here (Drive details, Application details) are read-only popups
  with no interactive Bootstrap components (carousels, dropdowns) that would justify the extra script.
  A `v-if` toggle is less code and one fewer script tag.
- **Alternatives considered**: Loading Bootstrap's JS bundle via CDN and using its native modal
  component — rejected as an unnecessary added dependency for two static, read-only popups.

## Decision: Section 2's five subsections are collapsible via a hand-rolled `CollapsibleSection.vue`

- **Decision**: A small shared component (Bootstrap `.card`/`.card-header`/`.card-body` classes, a
  clickable header, content toggled with plain `v-show` bound to internal state) wraps each of
  Section 2's five subsections. Section 1 is not wrapped in it — only Section 2's subsections are
  collapsible, per direct request.
- **Rationale**: Same reasoning as `Modal.vue`'s no-JS-bundle decision above — a click-to-toggle
  `v-show` is simpler than wiring Bootstrap's `data-bs-toggle="collapse"` JS behavior for what's a
  plain show/hide, and keeps the "Bootstrap for CSS, not JS" line consistent across the whole
  dashboard rather than adding the JS bundle for this one feature and not the modals.
- **Alternatives considered**: Bootstrap's native collapse component (`data-bs-toggle="collapse"`,
  requiring the JS bundle) — rejected for the same reason the modal's JS-bundle alternative was
  rejected; introducing the bundle for one feature after deliberately avoiding it for another would be
  an inconsistent, one-off exception.

## Decision: Dashboard's Companies total counts only approved Companies

- **Decision**: `GET /api/admin/dashboard`'s `companies` field is
  `Company.query.filter_by(approval_status="approved").count()`, not a raw `Company.query.count()`.
- **Rationale**: Bug found in review — the first implementation counted every Company row (pending,
  approved, and rejected alike), which visibly disagreed with Registered Companies' own count on the
  same page (e.g. showing "3" in the totals strip while Registered Companies listed only 2). A total
  that contradicts the one list it sits next to is actively misleading, not just imprecise.
- **Alternatives considered**: Leaving it as a raw count of every Company row and re-labeling it "All
  Companies" instead of fixing the number — rejected; a pending or rejected Company isn't a company
  in the sense any other part of this dashboard treats it (it can't create Drives, it isn't
  "Registered"), so counting it here has no use that outweighs the confusion it caused.

## Decision: Company approve/reject stays a single "decision" endpoint (unchanged from original draft)

- **Decision**: `POST /api/admin/companies/<id>/decision` with `{"status": "approved" | "rejected"}`
  is unchanged — Company Applications' Approve (green) and the newly-added Reject button both call it.
- **Rationale**: Direct product clarification confirmed Reject should exist alongside Approve
  ("for completeness... we have an option to blacklist anyway" was about a different, later state) —
  the one-endpoint-two-values design from the original draft already supports this with no change.
- **Alternatives considered**: N/A — reconfirmed, not revisited.

## Decision: Photo/logo/resume served as plain static files, no dedicated upload/download routes

- **Decision**: `Student.photo_path`, `Student.resume_path`, `Company.logo_path` are relative paths
  under `app/static/uploads/`, exposed to the frontend as `url_for('static', filename=...)` URLs. The
  Student Applications modal's "View Resume" is a plain `<a href="..." download>` — no dedicated
  authenticated download endpoint.
- **Rationale**: No upload mechanism exists yet (Milestones 4/5 add Company's/Student's own
  dashboards, where real uploads would happen) — for now these are seeded placeholder files. Since
  Flask already serves `app/static/` unauthenticated (the built Vue bundle lives there too), adding a
  separate authenticated route to gate access to a demo placeholder file would be complexity with no
  real security benefit yet; the HTML5 `download` attribute is enough to trigger a browser download
  from a same-origin static URL.
- **Alternatives considered**: A dedicated `GET /api/admin/students/<id>/resume` route using
  `send_file` — deferred until there's an actual reason to restrict access (e.g. once real resumes
  exist post-Milestone-5); premature now.
