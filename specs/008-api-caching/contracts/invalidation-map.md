# Contract: Cache invalidation map

This is the correctness contract for this milestone: every write below MUST call
`invalidate(namespace)` for every namespace listed, in the same request, before returning.
If a future change adds a new write path that affects one of the four cached listings, it
MUST be added here and to the corresponding route.

| Write (file, function) | Invalidates namespace(s) | Why |
|---|---|---|
| `company.py`, `create_drive` | `drives` | A new ongoing Drive should appear in Student drive listings immediately |
| `company.py`, `complete_drive` | `drives` | A closed Drive should disappear from Student drive listings immediately |
| `admin.py`, `decide_company` | `admin_companies`, `orgs`, `drives` | Changes `Company.approval_status`, which is read directly by `list_companies` (admin) and gates visibility in `list_organizations` and `list_drives` (Student) |
| `admin.py`, `toggle_active` | `admin_companies`, `admin_students` | Changes `User.is_active`, shown in both `list_companies` and `list_students` payloads; invalidating both unconditionally is simpler and just as correct as branching on the target's role |
| `student.py`, `update_profile` | `admin_students` | Changes fields (`name`, `contact`, `photo_path`, `resume_path`) shown in `list_students`' payload and searched by its `?q=` filter |

## Endpoints that read from cache (unaffected by any write not listed above)

| Endpoint | Namespace |
|---|---|
| `GET /student/drives` | `drives` |
| `GET /student/organizations` | `orgs` |
| `GET /admin/companies` | `admin_companies` |
| `GET /admin/students` | `admin_students` |

## Explicitly out of scope for this milestone

- `GET /company/drives` (a Company's own drive list) — not one of the milestone's named
  targets; low read volume (scoped to one Company), not worth the added invalidation surface.
- `GET /admin/job-positions`, `GET /admin/applications`, `GET /company/drives/<id>/applications`
  — none are in the milestone's explicit "job listings, company search, student search" list.
