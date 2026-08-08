from datetime import date, datetime

from flask import Blueprint, abort, jsonify, request
from flask_login import current_user
from sqlalchemy.orm import joinedload

from app import db
from app.constants import (
    APPLICATION_DECISION_STATUSES,
    APPLICATION_STATUS_PLACED,
    EXPORT_JOB_TYPE_CSV_EXPORT,
    EXPORT_JOB_TYPE_PLACEMENT_REPORT,
    JOB_POSITION_STATUS_COMPLETED,
    TERMINAL_APPLICATION_STATUSES,
)
from app.decorators import company_approved_required
from app.models import Application, ExportJob, JobPosition, Placement
from app.utils import export_job_payload, get_logger, iso_or_none, static_url

company_bp = Blueprint("company", __name__, url_prefix="/api/company")

logger = get_logger(__name__)


def _own_drive_or_404(drive_id):
    drive = JobPosition.query.get(drive_id)
    if drive is None or drive.company_id != current_user.company_profile.id:
        abort(404)
    return drive


def _own_application_or_404(application_id):
    application = Application.query.get(application_id)
    if (
        application is None
        or application.job_position.company_id != current_user.company_profile.id
    ):
        abort(404)
    return application


def _drive_payload(drive):
    return {
        "id": drive.id,
        "drive_name": drive.drive_name,
        "title": drive.title,
        "description": drive.description,
        "eligibility_criteria": drive.eligibility_criteria,
        "salary": drive.salary,
        "location": drive.location,
        "status": drive.status,
        "application_deadline": drive.application_deadline.isoformat(),
    }


def _application_summary_payload(application):
    return {
        "id": application.id,
        "student_name": application.student.name,
        "status": application.status,
        "application_date": application.application_date.isoformat(),
    }


def _application_detail_payload(application):
    student = application.student
    drive = application.job_position
    return {
        "id": application.id,
        "student_name": student.name,
        "student_branch": student.branch.name if student.branch else None,
        "student_cgpa": student.cgpa,
        "student_skills": [s.name for s in student.skills],
        "student_graduation_year": student.graduation_year,
        "student_contact": student.contact,
        "student_photo_url": static_url(student.photo_path),
        "student_resume_url": static_url(student.resume_path),
        "drive_name": drive.drive_name,
        "job_title": drive.title,
        "status": application.status,
        "interview_datetime": iso_or_none(application.interview_datetime),
        "interview_mode": application.interview_mode,
        "company_remark": application.company_remark,
    }


@company_bp.route("/drives", methods=["POST"])
@company_approved_required
def create_drive():
    data = request.get_json(silent=True) or {}
    drive_name = data.get("drive_name")
    title = data.get("title")
    application_deadline = data.get("application_deadline")

    if not all([drive_name, title, application_deadline]):
        return (
            jsonify(
                {"error": "drive_name, title and application_deadline are required"}
            ),
            400,
        )

    try:
        deadline = datetime.fromisoformat(application_deadline)
    except ValueError:
        return (
            jsonify({"error": "application_deadline must be a valid ISO datetime"}),
            400,
        )

    drive = JobPosition(
        company_id=current_user.company_profile.id,
        drive_name=drive_name,
        title=title,
        description=data.get("description"),
        eligibility_criteria=data.get("eligibility_criteria"),
        salary=data.get("salary"),
        location=data.get("location"),
        application_deadline=deadline,
    )
    db.session.add(drive)
    db.session.commit()
    logger.info(
        "Drive created: drive_id=%s company_id=%s title=%s",
        drive.id,
        drive.company_id,
        title,
    )
    return jsonify(_drive_payload(drive)), 201


@company_bp.route("/drives", methods=["GET"])
@company_approved_required
def list_drives():
    query = JobPosition.query.filter_by(company_id=current_user.company_profile.id)

    status = request.args.get("status")
    if status:
        query = query.filter(JobPosition.status == status)

    return jsonify([_drive_payload(d) for d in query.all()]), 200


@company_bp.route("/drives/<int:drive_id>/complete", methods=["POST"])
@company_approved_required
def complete_drive(drive_id):
    drive = _own_drive_or_404(drive_id)
    drive.status = JOB_POSITION_STATUS_COMPLETED
    db.session.commit()
    logger.info("Drive closed: drive_id=%s company_id=%s", drive.id, drive.company_id)
    return jsonify({"id": drive.id, "status": drive.status}), 200


@company_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
@company_approved_required
def list_drive_applications(drive_id):
    drive = _own_drive_or_404(drive_id)
    applications = (
        Application.query.options(joinedload(Application.student))
        .filter_by(job_position_id=drive.id)
        .all()
    )

    status = request.args.get("status")
    if status:
        applications = [a for a in applications if a.status == status]

    if request.args.get("sort") == "status":
        applications = sorted(applications, key=lambda a: a.status)

    return jsonify([_application_summary_payload(a) for a in applications]), 200


@company_bp.route("/applications/<int:application_id>", methods=["GET"])
@company_approved_required
def get_application(application_id):
    application = _own_application_or_404(application_id)
    return jsonify(_application_detail_payload(application)), 200


@company_bp.route("/applications/<int:application_id>/decision", methods=["POST"])
@company_approved_required
def decide_application(application_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in APPLICATION_DECISION_STATUSES:
        return (
            jsonify(
                {
                    "error": "status must be one of "
                    + ", ".join(APPLICATION_DECISION_STATUSES)
                }
            ),
            400,
        )

    application = _own_application_or_404(application_id)
    if application.status in TERMINAL_APPLICATION_STATUSES:
        logger.warning(
            "Decision rejected (final outcome): application_id=%s current_status=%s attempted_status=%s",
            application.id,
            application.status,
            status,
        )
        return jsonify({"error": "This application's outcome is final"}), 409

    previous_status = application.status

    if status == APPLICATION_STATUS_PLACED:
        position_title = data.get("position_title")
        joining_date = data.get("joining_date")
        if not position_title or not joining_date:
            return (
                jsonify(
                    {
                        "error": "position_title and joining_date are required to mark Placed"
                    }
                ),
                400,
            )
        try:
            joining_date = date.fromisoformat(joining_date)
        except ValueError:
            return jsonify({"error": "joining_date must be a valid ISO date"}), 400

        placement = Placement(
            student_id=application.student_id,
            company_id=application.job_position.company_id,
            application_id=application.id,
            position_title=position_title,
            salary=data.get("salary"),
            joining_date=joining_date,
        )
        db.session.add(placement)
        logger.info(
            "Placement created: application_id=%s student_id=%s company_id=%s position_title=%s",
            application.id,
            application.student_id,
            application.job_position.company_id,
            position_title,
        )

    application.status = status
    remark = data.get("remark")
    if remark is not None:
        application.company_remark = remark
    db.session.commit()
    logger.info(
        "Application status changed: application_id=%s %s -> %s",
        application.id,
        previous_status,
        status,
    )

    return (
        jsonify(
            {
                "id": application.id,
                "status": application.status,
                "remark": application.company_remark,
            }
        ),
        200,
    )


@company_bp.route("/applications/<int:application_id>/interview", methods=["POST"])
@company_approved_required
def schedule_interview(application_id):
    data = request.get_json(silent=True) or {}
    interview_datetime = data.get("interview_datetime")
    if not interview_datetime:
        return jsonify({"error": "interview_datetime is required"}), 400

    try:
        parsed = datetime.fromisoformat(interview_datetime)
    except ValueError:
        return (
            jsonify({"error": "interview_datetime must be a valid ISO datetime"}),
            400,
        )

    application = _own_application_or_404(application_id)
    application.interview_datetime = parsed
    mode = data.get("mode")
    if mode is not None:
        application.interview_mode = mode
    db.session.commit()
    logger.info(
        "Interview scheduled: application_id=%s interview_datetime=%s mode=%s",
        application.id,
        application.interview_datetime.isoformat(),
        mode,
    )

    return (
        jsonify(
            {
                "id": application.id,
                "interview_datetime": application.interview_datetime.isoformat(),
                "mode": application.interview_mode,
            }
        ),
        200,
    )


@company_bp.route("/exports", methods=["POST"])
@company_approved_required
def create_export():
    # Deferred import: app.tasks -> app.celery_app -> create_app() -> this
    # blueprint would be circular if imported at module level.
    from app.tasks import process_export_job

    job = ExportJob(user_id=current_user.id, job_type=EXPORT_JOB_TYPE_CSV_EXPORT)
    db.session.add(job)
    db.session.commit()

    try:
        process_export_job.delay(job.id)
    except Exception:
        logger.exception("Could not enqueue export job_id=%s", job.id)
        return (
            jsonify(
                {
                    "error": "Export could not be scheduled - background jobs are unavailable"
                }
            ),
            503,
        )

    logger.info("Export job created: job_id=%s company_id=%s", job.id, current_user.id)
    return jsonify(export_job_payload(job)), 202


@company_bp.route("/exports", methods=["GET"])
@company_approved_required
def list_exports():
    jobs = (
        ExportJob.query.filter_by(
            user_id=current_user.id, job_type=EXPORT_JOB_TYPE_CSV_EXPORT
        )
        .order_by(ExportJob.created_at.desc())
        .all()
    )
    return jsonify([export_job_payload(j) for j in jobs]), 200


@company_bp.route("/exports/<int:job_id>", methods=["GET"])
@company_approved_required
def get_export(job_id):
    job = ExportJob.query.filter_by(
        id=job_id, user_id=current_user.id, job_type=EXPORT_JOB_TYPE_CSV_EXPORT
    ).first()
    if job is None:
        return jsonify({"error": "Export not found"}), 404
    return jsonify(export_job_payload(job)), 200


@company_bp.route("/reports", methods=["GET"])
@company_approved_required
def list_reports():
    jobs = (
        ExportJob.query.filter_by(
            user_id=current_user.id, job_type=EXPORT_JOB_TYPE_PLACEMENT_REPORT
        )
        .order_by(ExportJob.created_at.desc())
        .all()
    )
    return jsonify([export_job_payload(j) for j in jobs]), 200


@company_bp.route("/reports/<int:job_id>", methods=["GET"])
@company_approved_required
def get_report(job_id):
    job = ExportJob.query.filter_by(
        id=job_id, user_id=current_user.id, job_type=EXPORT_JOB_TYPE_PLACEMENT_REPORT
    ).first()
    if job is None:
        return jsonify({"error": "Report not found"}), 404
    return jsonify(export_job_payload(job)), 200
