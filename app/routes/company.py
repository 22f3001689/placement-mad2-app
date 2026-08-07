from datetime import datetime

from flask import Blueprint, abort, jsonify, request
from flask_login import current_user

from app import db
from app.decorators import company_approved_required
from app.models import Application, JobPosition
from app.utils import static_url

company_bp = Blueprint("company", __name__, url_prefix="/api/company")

APPLICATION_DECISION_STATUSES = ("shortlisted", "waiting", "selected", "rejected")


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
        "student_branch": student.branch,
        "student_photo_url": static_url(student.photo_path),
        "student_resume_url": static_url(student.resume_path),
        "drive_name": drive.drive_name,
        "job_title": drive.title,
        "status": application.status,
        "interview_datetime": (
            application.interview_datetime.isoformat()
            if application.interview_datetime
            else None
        ),
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
        return jsonify(
            {"error": "drive_name, title and application_deadline are required"}
        ), 400

    try:
        deadline = datetime.fromisoformat(application_deadline)
    except ValueError:
        return jsonify({"error": "application_deadline must be a valid ISO datetime"}), 400

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
    drive.status = "completed"
    db.session.commit()
    return jsonify({"id": drive.id, "status": drive.status}), 200


@company_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
@company_approved_required
def list_drive_applications(drive_id):
    drive = _own_drive_or_404(drive_id)
    applications = drive.applications

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
        return jsonify(
            {"error": "status must be one of shortlisted, waiting, selected, rejected"}
        ), 400

    application = _own_application_or_404(application_id)
    application.status = status
    remark = data.get("remark")
    if remark is not None:
        application.company_remark = remark
    db.session.commit()

    payload = {"id": application.id, "status": application.status}
    if remark is not None:
        payload["remark"] = application.company_remark
    return jsonify(payload), 200


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
        return jsonify({"error": "interview_datetime must be a valid ISO datetime"}), 400

    application = _own_application_or_404(application_id)
    application.interview_datetime = parsed
    mode = data.get("mode")
    if mode is not None:
        application.interview_mode = mode
    db.session.commit()

    payload = {
        "id": application.id,
        "interview_datetime": application.interview_datetime.isoformat(),
    }
    if mode is not None:
        payload["mode"] = application.interview_mode
    return jsonify(payload), 200
