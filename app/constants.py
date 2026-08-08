"""Single source of truth for the app's fixed status/approval vocabularies.

Kept as plain tuples (not a DB-level enum/CHECK constraint) to match this
project's existing pattern of validating these at the route layer.
"""

APPLICATION_STATUSES = (
    "applied",
    "shortlisted",
    "interview",
    "offer",
    "rejected",
    "placed",
)
TERMINAL_APPLICATION_STATUSES = ("placed", "rejected")

JOB_POSITION_STATUSES = ("ongoing", "completed")

COMPANY_APPROVAL_STATUSES = ("pending", "approved", "rejected")
