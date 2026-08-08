# Data Model: API Performance Optimization and Caching

No SQL schema changes — nothing new in `app/models.py`, no migration. The only "data model"
here is the shape of a cache entry in Redis, which is not a SQLAlchemy model.

## Cache entry (Redis, not SQL)

| Field | Description |
|---|---|
| Key | `cache:<namespace>:<raw query string>` — see research.md |
| Value | The exact JSON response body the view would have returned, stored as raw bytes |
| TTL | `CACHE_DEFAULT_TTL` seconds (config, default 60) — safety-net expiry independent of explicit invalidation |

## Namespaces (one per target endpoint)

| Namespace | Endpoint | Invalidated by |
|---|---|---|
| `drives` | `GET /student/drives` | Company create/complete Drive; Admin approve/reject Company (approval gates Student-visible drives) |
| `orgs` | `GET /student/organizations` | Admin approve/reject Company |
| `admin_companies` | `GET /admin/companies` | Admin approve/reject Company; Admin toggle-active (on a Company account) |
| `admin_students` | `GET /admin/students` | Admin toggle-active (on a Student account); Student profile update |

See `contracts/invalidation-map.md` for the exact call-site-to-namespace mapping.
