"""Celery tasks: interview reminders, CSV/report exports.

Each task runs inside the Flask app context (see app/celery_app.py's
FlaskTask), so db.session/current_app work exactly like in a request.
"""

import csv
import os
from collections import Counter
from datetime import datetime, timedelta

from flask import current_app

from app import db
from app.celery_app import celery
from app.constants import (
    COMPANY_APPROVAL_APPROVED,
    EXPORT_JOB_STATUS_FAILED,
    EXPORT_JOB_STATUS_READY,
    EXPORT_JOB_STATUS_RUNNING,
    EXPORT_JOB_TYPE_CSV_EXPORT,
    EXPORT_JOB_TYPE_PLACEMENT_REPORT,
    ROLE_STUDENT,
    TERMINAL_APPLICATION_STATUSES,
)
from app.models import Application, Company, ExportJob, JobPosition, Placement
from app.notifications import send_email
from app.utils import (
    get_logger,
    iso_or_none,
    placement_payloads_by_application_id,
    static_path,
)

logger = get_logger(__name__)

INTERVIEW_REMINDER_LOOKAHEAD = timedelta(hours=24)
EXPORTS_DIR = "exports"
REPORTS_DIR = "reports"

CSV_HEADERS = [
    "job_title",
    "company_name",
    "student_name",
    "status",
    "application_date",
    "interview_datetime",
    "placement_position_title",
    "placement_salary",
    "placement_joining_date",
]


@celery.task
def send_interview_reminders():
    """Reminds each Student, once, of an upcoming interview (see FR-001/FR-007)."""
    now = datetime.utcnow()
    applications = Application.query.filter(
        Application.interview_datetime.isnot(None),
        Application.interview_datetime >= now,
        Application.interview_datetime <= now + INTERVIEW_REMINDER_LOOKAHEAD,
        Application.interview_reminded_at.is_(None),
        ~Application.status.in_(TERMINAL_APPLICATION_STATUSES),
    ).all()

    for application in applications:
        student = application.student
        drive = application.job_position
        send_email(
            student.user.email,
            "interview_reminder",
            {
                "student_name": student.name,
                "company_name": drive.company.company_name,
                "job_title": drive.title,
                "interview_datetime": iso_or_none(application.interview_datetime),
            },
        )
        application.interview_reminded_at = now
        db.session.commit()
        logger.info(
            "Interview reminder sent: application_id=%s student_id=%s",
            application.id,
            student.id,
        )


def _export_row(application, placements_by_application_id):
    placement = placements_by_application_id.get(application.id) or {}
    return [
        application.job_position.title,
        application.job_position.company.company_name,
        application.student.name,
        application.status,
        iso_or_none(application.application_date),
        iso_or_none(application.interview_datetime),
        placement.get("position_title", ""),
        placement.get("salary", ""),
        placement.get("joining_date", ""),
    ]


def _applications_for_export(user):
    if user.role == ROLE_STUDENT:
        return user.student_profile.applications
    return (
        Application.query.join(JobPosition)
        .filter(JobPosition.company_id == user.company_profile.id)
        .all()
    )


def _write_csv_export(job):
    applications = _applications_for_export(job.user)
    placements_by_application_id = placement_payloads_by_application_id(applications)

    filename = f"{job.user_id}_{job.id}.csv"
    relative_path = f"{EXPORTS_DIR}/{filename}"
    full_path = os.path.join(current_app.static_folder, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        for application in applications:
            writer.writerow(_export_row(application, placements_by_application_id))

    job.file_path = relative_path


@celery.task
def process_export_job(job_id):
    """Runs a user-triggered CSV export job (see FR-003/FR-005)."""
    job = ExportJob.query.get(job_id)
    if job is None:
        logger.warning("process_export_job called with unknown job_id=%s", job_id)
        return

    job.status = EXPORT_JOB_STATUS_RUNNING
    db.session.commit()

    try:
        if job.job_type == EXPORT_JOB_TYPE_CSV_EXPORT:
            _write_csv_export(job)
        else:
            raise ValueError(
                f"Unsupported job_type for process_export_job: {job.job_type}"
            )

        job.status = EXPORT_JOB_STATUS_READY
        job.completed_at = datetime.utcnow()
        db.session.commit()

        send_email(
            job.user.email,
            "export_ready",
            {"name": job.user.username, "download_url": static_path(job.file_path)},
        )
        logger.info(
            "Export job completed: job_id=%s file_path=%s", job.id, job.file_path
        )
    except Exception:
        db.session.rollback()
        job.status = EXPORT_JOB_STATUS_FAILED
        job.error_message = "Export failed - see server logs for details"
        job.completed_at = datetime.utcnow()
        db.session.commit()
        logger.exception("Export job failed: job_id=%s", job.id)


def _write_placement_report_html(job, company, applications, status_counts, placements):
    filename = f"{job.user_id}_{job.id}.html"
    relative_path = f"{REPORTS_DIR}/{filename}"
    full_path = os.path.join(current_app.static_folder, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    status_rows = "".join(
        f"<tr><td>{status}</td><td>{count}</td></tr>"
        for status, count in status_counts.items()
    )
    placement_rows = "".join(
        f"<tr><td>{p.position_title}</td><td>{p.salary}</td><td>{p.joining_date}</td></tr>"
        for p in placements
    )
    html = (
        "<!DOCTYPE html><html><head>"
        f"<title>Placement Report - {company.company_name}</title></head><body>"
        f"<h1>Placement Report: {company.company_name}</h1>"
        f"<p>Period: {job.period_start} to {job.period_end}</p>"
        f"<h2>Applications by Status (Total: {len(applications)})</h2>"
        f"<table border='1'><tr><th>Status</th><th>Count</th></tr>{status_rows}</table>"
        f"<h2>Placements in this period ({len(placements)})</h2>"
        "<table border='1'><tr><th>Position</th><th>Salary</th><th>Joining Date</th></tr>"
        f"{placement_rows}</table></body></html>"
    )

    with open(full_path, "w") as f:
        f.write(html)

    job.file_path = relative_path


@celery.task
def generate_placement_reports():
    """Generates one HTML placement report per Company per reporting period,
    skipping Companies with no data to report (see FR-006/FR-007).
    """
    companies = Company.query.filter_by(approval_status=COMPANY_APPROVAL_APPROVED).all()

    for company in companies:
        applications = (
            Application.query.join(JobPosition)
            .filter(JobPosition.company_id == company.id)
            .all()
        )
        if not applications:
            continue

        last_report = (
            ExportJob.query.filter_by(
                user_id=company.user_id, job_type=EXPORT_JOB_TYPE_PLACEMENT_REPORT
            )
            .order_by(ExportJob.period_end.desc())
            .first()
        )
        period_start = (
            last_report.period_end if last_report else company.created_at.date()
        )
        period_end = datetime.utcnow().date()
        if period_start >= period_end:
            continue

        placements = [
            p
            for p in Placement.query.filter_by(company_id=company.id).all()
            if period_start <= p.created_at.date() <= period_end
        ]
        status_counts = Counter(a.status for a in applications)

        job = ExportJob(
            user_id=company.user_id,
            job_type=EXPORT_JOB_TYPE_PLACEMENT_REPORT,
            status=EXPORT_JOB_STATUS_READY,
            period_start=period_start,
            period_end=period_end,
            completed_at=datetime.utcnow(),
        )
        db.session.add(job)
        db.session.flush()

        _write_placement_report_html(
            job, company, applications, status_counts, placements
        )
        db.session.commit()

        send_email(
            company.user.email,
            "report_ready",
            {
                "company_name": company.company_name,
                "download_url": static_path(job.file_path),
                "period_start": iso_or_none(period_start),
                "period_end": iso_or_none(period_end),
            },
        )
        logger.info(
            "Placement report generated: company_id=%s job_id=%s period=%s..%s",
            company.id,
            job.id,
            period_start,
            period_end,
        )
