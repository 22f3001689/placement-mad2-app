from flask import url_for

from app.constants import APPLICATION_STATUS_PLACED
from app.models import Placement


def static_url(path):
    """Builds a URL for a file under app/static/, or None if path is falsy."""
    return url_for("static", filename=path) if path else None


def branch_payload(branch):
    return {
        "id": branch.id,
        "code": branch.code,
        "name": branch.name,
        "description": branch.description,
    }


def placement_payloads_by_application_id(applications):
    """Batch-loads Placements for a list of Applications in one query.

    Returns {application_id: {position_title, salary, joining_date}} for
    every Placed application that has one - avoids one query per application.
    """
    placed_ids = [a.id for a in applications if a.status == APPLICATION_STATUS_PLACED]
    if not placed_ids:
        return {}

    placements = Placement.query.filter(Placement.application_id.in_(placed_ids)).all()
    return {
        p.application_id: {
            "position_title": p.position_title,
            "salary": p.salary,
            "joining_date": p.joining_date.isoformat() if p.joining_date else None,
        }
        for p in placements
    }
