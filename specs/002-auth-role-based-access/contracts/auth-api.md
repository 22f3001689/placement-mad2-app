# Auth API Contract

Base path: `/api/auth`. All requests/responses are JSON. The session cookie set on login is sent
automatically by the browser on every subsequent request (`fetch(..., { credentials: 'include' })`
on the frontend side) — no token is returned to or stored by the client.

## POST /api/auth/register/student

**Request**:
```json
{ "username": "john_doe", "password": "secret123", "name": "John Doe" }
```

**Responses**:
- `201` — `{ "username": "john_doe", "role": "student" }`
- `400` — missing field or password under 6 characters: `{ "error": "..." }`
- `409` — username already taken: `{ "error": "Username already exists" }`

## POST /api/auth/register/company

**Request**:
```json
{ "username": "acme_corp", "password": "secret123", "company_name": "Acme Corp" }
```

**Responses**:
- `201` — `{ "username": "acme_corp", "role": "company", "approval_status": "pending" }`
- `400` — missing field or password under 6 characters: `{ "error": "..." }`
- `409` — username already taken: `{ "error": "Username already exists" }`

Note: there is no `/api/auth/register/admin` — no such endpoint exists, by design (FR-003).

## POST /api/auth/login

**Request**:
```json
{ "username": "john_doe", "password": "secret123" }
```

**Responses**:
- `200` — sets the session cookie; body reflects role and, for a company, its approval status:
  ```json
  { "username": "john_doe", "role": "student" }
  ```
  ```json
  { "username": "acme_corp", "role": "company", "approval_status": "pending" }
  ```
- `401` — wrong username or wrong password (same message either way, FR-006):
  `{ "error": "Invalid username or password" }`
- `403` — credentials correct but the account is deactivated/blacklisted (FR-005):
  `{ "error": "This account has been deactivated" }`

## POST /api/auth/logout

Requires an active session.

**Responses**:
- `200` — `{ "message": "Logged out" }`; session cookie is cleared.
- `401` — no active session: `{ "error": "Not logged in" }`

## GET /api/auth/me

Requires an active session. Used by the frontend on page load to restore auth state and by role
guards to check the current user before entering a protected route.

**Responses**:
- `200` —
  ```json
  { "username": "john_doe", "role": "student" }
  ```
  or, for a company:
  ```json
  { "username": "acme_corp", "role": "company", "approval_status": "approved" }
  ```
- `401` — no active session: `{ "error": "Not logged in" }`

## Role-gated endpoints in general (applies to every endpoint added from Milestone 3 onward)

- No active session → `401`.
- Active session, wrong role for this endpoint → `403`.
- Active Company session, but the endpoint requires `approval_status == "approved"` and it isn't →
  `403` with a body distinguishing this from a plain role mismatch:
  `{ "error": "Company is not yet approved" }`.
