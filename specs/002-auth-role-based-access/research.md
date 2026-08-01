# Phase 0 Research: Authentication & Role-Based Access

No open `[NEEDS CLARIFICATION]` markers were left in the spec — the decisions below resolve every
technical unknown the Technical Context flagged.

## Decision: Session cookies via Flask-Login, not JWT

- **Decision**: Use Flask-Login (`login_user`, `logout_user`, `login_required`, `current_user`)
  exactly as `../hms-app-main` does, rather than issuing JWTs.
- **Rationale**: The project statement allows either ("Flask security (session or token) or JWT
  based Token"), so this is a real choice, not a mandate. Milestone 1 already added `UserMixin` and
  `login.user_loader` to the `User` model specifically so this milestone could reuse Flask-Login
  directly — reversing that now would mean touching `app/models.py` again for no benefit. JWT's usual
  advantage (avoiding cross-origin cookie/CORS pain between a separately-hosted SPA and API) doesn't
  apply here: the Vite dev server proxies `/api/*` to Flask during development, and Flask serves the
  built Vue bundle itself in the local-demo run mode — both are same-origin, so plain session cookies
  work with zero CORS configuration.
- **Alternatives considered**: JWT via a token library — rejected as unnecessary complexity (refresh-
  token handling, client-side token storage/XSS considerations) for a same-origin, local-demo-only
  app; would also contradict the Milestone 1 groundwork already merged.

## Decision: A small `role_required` decorator, diverging from the reference project's inline checks

- **Decision**: Add `app/decorators.py` with `role_required(*roles)`, wrapping `login_required` and
  an `abort(403)` role check into one reusable decorator.
- **Rationale**: See plan.md's Complexity Tracking — `../hms-app-main` inlines this check per-route
  because it only ever has ~15 routes total; this project's own milestone list adds role-gated
  endpoints across Milestones 3 through 8, where the duplication would be real, not hypothetical.
- **Alternatives considered**: Copy the reference project's inline `if current_user.role not in
  (...): abort(403)` per route — rejected once the scale of upcoming repetition is visible in the
  milestone doc itself.

## Decision: No Pinia, no axios on the frontend

- **Decision**: Auth state as one `reactive()` object in `frontend/src/state/auth.js`; HTTP calls via
  the browser's built-in `fetch`.
- **Rationale**: The entire shared state this milestone needs is "who's logged in, what's their
  role/approval status" — a single reactive object covers that without a state-management library.
  `fetch` covers 5 JSON endpoints with a five-line wrapper; axios's interceptors/instance config would
  be solving a problem (many endpoints, complex error handling) this milestone doesn't have yet.
- **Alternatives considered**: Pinia (the modern Vue-recommended store) — genuinely reasonable for a
  bigger app, but revisit only if/when state sharing gets more complex in a later milestone; adding
  it speculatively now would be exactly the kind of unrequested "flexibility" Principle VII warns
  against.

## Decision: Vue served through one Jinja shell + Vite building into `app/static/dist/`

- **Decision**: `vite.config.js` sets `build.outDir` to `../app/static/dist` and pins stable
  (non-hashed) output filenames; `app/templates/index.html` is a genuine Jinja template (uses
  `url_for('static', ...)`) that Flask renders for `/` and any non-`/api` path (a catch-all route),
  giving Vue Router's client-side routes something to land on after a browser refresh.
- **Rationale**: Satisfies the constitution's "Jinja2 only as a single entry-point shell, never for a
  UI view" literally — Jinja renders exactly one template, and it contains no UI markup beyond a
  mount point and the Bootstrap/script tags. Pinning stable filenames avoids needing a manifest.json
  parser in the Jinja template just to find the current build's hashed asset names.
- **Alternatives considered**: Serving Vite's default hashed-filename build and reading
  `manifest.json` from the Jinja template to resolve them — rejected as unnecessary machinery for a
  single-page, single-shell app with no cache-busting requirement stated anywhere in the project docs.

## Decision: No CORS library

- **Decision**: Add no `Flask-CORS` (or equivalent) dependency.
- **Rationale**: Both run modes described in Technical Context are same-origin from the browser's
  perspective (Vite dev proxy in dev, Flask serving the build directly in demo mode) — there is no
  cross-origin request to permit.
- **Alternatives considered**: N/A — no scenario in this milestone requires it.
