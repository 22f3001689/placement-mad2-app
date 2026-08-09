import logging

from flask import current_app, url_for

from app.constants import APPLICATION_STATUS_PLACED
from app.models import Placement, User

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s.%(funcName)s] %(message)s",
)


def get_logger(name):
    """Returns a logger scoped to the caller's module.

    Call as `get_logger(__name__)` at the top of a file - the configured
    format then stamps every line with that module (i.e. the file) and the
    function it was logged from, e.g. "app.routes.company.decide_application".
    """
    return logging.getLogger(name)


def static_url(path):
    """Builds a URL for a file under app/static/, or None if path is falsy."""
    return url_for("static", filename=path) if path else None


def static_path(path):
    """Same as static_url(), but usable outside a request context (e.g. in a
    Celery task) - url_for() needs an active request or SERVER_NAME to build
    URLs, neither of which a background task has.
    """
    return f"{current_app.static_url_path}/{path}" if path else None


def iso_or_none(value):
    """ISO-formats a date/datetime, or None if it's falsy."""
    return value.isoformat() if value else None


def default_email(name):
    """firstname.lastname@example.com derived from a full name, deduped on collision."""
    parts = name.lower().split()
    base = f"{parts[0]}.{parts[-1]}"
    email = f"{base}@example.com"
    suffix = 1
    while User.query.filter_by(email=email).first():
        suffix += 1
        email = f"{base}{suffix}@example.com"
    return email


def branch_payload(branch):
    return {
        "id": branch.id,
        "code": branch.code,
        "name": branch.name,
        "description": branch.description,
    }


def export_job_payload(job):
    return {
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "download_url": static_url(job.file_path),
        "period_start": iso_or_none(job.period_start),
        "period_end": iso_or_none(job.period_end),
        "created_at": iso_or_none(job.created_at),
        "completed_at": iso_or_none(job.completed_at),
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
            "joining_date": iso_or_none(p.joining_date),
        }
        for p in placements
    }
