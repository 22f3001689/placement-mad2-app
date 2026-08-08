import os

from flask import Blueprint, Response, current_app, jsonify, request
from flask_login import current_user
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from app import db
from app.constants import (
    COMPANY_APPROVAL_APPROVED,
    JOB_POSITION_STATUS_COMPLETED,
    JOB_POSITION_STATUS_ONGOING,
)
from app.decorators import role_required
from app.models import Application, Branch, Company, JobPosition, Placement, Skill
from app.utils import (
    branch_payload,
    get_logger,
    placement_payloads_by_application_id,
    static_url,
)

student_bp = Blueprint("student", __name__, url_prefix="/api/student")

logger = get_logger(__name__)

PHOTOS_DIR = "uploads/photos"
RESUMES_DIR = "uploads/resumes"


def _save_upload(file, subdir):
    filename = f"{current_user.id}_{secure_filename(file.filename)}"
    relative_path = f"{subdir}/{filename}"
    file.save(os.path.join(current_app.static_folder, relative_path))
    return relative_path


def _profile_payload(student):
    return {
        "name": student.name,
        "branch": branch_payload(student.branch) if student.branch else None,
        "graduation_year": student.graduation_year,
        "cgpa": student.cgpa,
        "skills": [{"id": s.id, "name": s.name} for s in student.skills],
        "contact": student.contact,
        "photo_url": static_url(student.photo_path),
        "resume_url": static_url(student.resume_path),
    }


def _organization_payload(company):
    return {
        "id": company.id,
        "company_name": company.company_name,
        "industry": company.industry,
        "logo_url": static_url(company.logo_path),
    }


def _organization_detail_payload(company):
    return {
        "id": company.id,
        "company_name": company.company_name,
        "overview": company.overview,
        "logo_url": static_url(company.logo_path),
        "industry": company.industry,
        "location": company.location,
    }


def _approved_drive_or_none(drive_id):
    """Returns the drive if it exists and its Company is currently approved, else None."""
    drive = JobPosition.query.get(drive_id)
    if drive is None or drive.company.approval_status != COMPANY_APPROVAL_APPROVED:
        return None
    return drive


def _drive_summary_payload(drive):
    return {
        "id": drive.id,
        "drive_name": drive.drive_name,
        "title": drive.title,
        "company_name": drive.company.company_name,
    }


def _drive_detail_payload(drive):
    already_applied = (
        Application.query.filter_by(
            student_id=current_user.student_profile.id, job_position_id=drive.id
        ).first()
        is not None
    )
    return {
        "id": drive.id,
        "drive_name": drive.drive_name,
        "title": drive.title,
        "description": drive.description,
        "eligibility_criteria": drive.eligibility_criteria,
        "salary": drive.salary,
        "location": drive.location,
        "company_name": drive.company.company_name,
        "company_logo_url": static_url(drive.company.logo_path),
        "status": drive.status,
        "already_applied": already_applied,
    }


def _application_payload(application, placements_by_application_id):
    return {
        "id": application.id,
        "job_position_id": application.job_position_id,
        "drive_name": application.job_position.drive_name,
        "job_title": application.job_position.title,
        "company_name": application.job_position.company.company_name,
        "status": application.status,
        "interview_datetime": (
            application.interview_datetime.isoformat()
            if application.interview_datetime
            else None
        ),
        "interview_mode": application.interview_mode,
        "company_remark": application.company_remark,
        "application_date": application.application_date.isoformat(),
        "placement": placements_by_application_id.get(application.id),
    }


@student_bp.route("/profile", methods=["GET"])
@role_required("student")
def get_profile():
    return jsonify(_profile_payload(current_user.student_profile)), 200


@student_bp.route("/profile", methods=["POST"])
@role_required("student")
def update_profile():
    student = current_user.student_profile
    form = request.form

    if "name" in form:
        student.name = form["name"]
    if "branch_id" in form:
        branch = Branch.query.get(form["branch_id"])
        if branch is None:
            return jsonify({"error": "branch_id must be a valid Branch"}), 400
        student.branch_id = branch.id
    if "graduation_year" in form:
        try:
            student.graduation_year = int(form["graduation_year"])
        except ValueError:
            return jsonify({"error": "graduation_year must be a whole number"}), 400
    if "cgpa" in form:
        try:
            student.cgpa = float(form["cgpa"])
        except ValueError:
            return jsonify({"error": "cgpa must be a number"}), 400
    if "skill_ids" in form:
        skill_ids = form.getlist("skill_ids")
        skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
        if len(skills) != len(set(skill_ids)):
            return jsonify({"error": "skill_ids must all be valid Skills"}), 400
        student.skills = skills
    if "contact" in form:
        student.contact = form["contact"]

    photo = request.files.get("photo")
    if photo and photo.filename:
        student.photo_path = _save_upload(photo, PHOTOS_DIR)
        logger.info(
            "Profile photo uploaded: student_id=%s path=%s",
            student.id,
            student.photo_path,
        )

    resume = request.files.get("resume")
    if resume and resume.filename:
        student.resume_path = _save_upload(resume, RESUMES_DIR)
        logger.info(
            "Resume uploaded: student_id=%s path=%s", student.id, student.resume_path
        )

    db.session.commit()
    logger.info("Profile updated: student_id=%s", student.id)
    return jsonify(_profile_payload(student)), 200


@student_bp.route("/organizations", methods=["GET"])
@role_required("student")
def list_organizations():
    query = Company.query.filter_by(approval_status=COMPANY_APPROVAL_APPROVED)

    q = request.args.get("q")
    if q:
        query = query.filter(Company.company_name.ilike(f"%{q}%"))

    return jsonify([_organization_payload(c) for c in query.all()]), 200


@student_bp.route("/organizations/<int:company_id>", methods=["GET"])
@role_required("student")
def get_organization(company_id):
    company = Company.query.filter_by(
        id=company_id, approval_status=COMPANY_APPROVAL_APPROVED
    ).first()
    if company is None:
        return jsonify({"error": "Company not found"}), 404

    return jsonify(_organization_detail_payload(company)), 200


@student_bp.route("/drives", methods=["GET"])
@role_required("student")
def list_drives():
    query = (
        JobPosition.query.join(Company, JobPosition.company_id == Company.id)
        .filter(JobPosition.status == JOB_POSITION_STATUS_ONGOING)
        .filter(Company.approval_status == COMPANY_APPROVAL_APPROVED)
    )

    company_id = request.args.get("company_id")
    if company_id:
        query = query.filter(JobPosition.company_id == company_id)

    q = request.args.get("q")
    if q:
        query = query.filter(
            or_(
                Company.company_name.ilike(f"%{q}%"),
                JobPosition.title.ilike(f"%{q}%"),
                JobPosition.drive_name.ilike(f"%{q}%"),
                JobPosition.skills_required.ilike(f"%{q}%"),
            )
        )

    return jsonify([_drive_summary_payload(d) for d in query.all()]), 200


@student_bp.route("/drives/<int:drive_id>", methods=["GET"])
@role_required("student")
def get_drive(drive_id):
    drive = _approved_drive_or_none(drive_id)
    if drive is None:
        return jsonify({"error": "Drive not found"}), 404

    return jsonify(_drive_detail_payload(drive)), 200


@student_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@role_required("student")
def apply_to_drive(drive_id):
    drive = _approved_drive_or_none(drive_id)
    if drive is None:
        return jsonify({"error": "Drive not found"}), 404

    if drive.status == JOB_POSITION_STATUS_COMPLETED:
        return jsonify({"error": "This Drive is no longer accepting applications"}), 409

    student_id = current_user.student_profile.id
    existing = Application.query.filter_by(
        student_id=student_id, job_position_id=drive_id
    ).first()
    if existing is not None:
        return jsonify({"error": "You have already applied to this Drive"}), 409

    application = Application(student_id=student_id, job_position_id=drive_id)
    db.session.add(application)
    db.session.commit()
    logger.info(
        "Application submitted: application_id=%s student_id=%s job_position_id=%s",
        application.id,
        student_id,
        drive_id,
    )
    return jsonify({"id": application.id, "status": application.status}), 201


@student_bp.route("/applications", methods=["GET"])
@role_required("student")
def list_applications():
    applications = current_user.student_profile.applications
    placements_by_application_id = placement_payloads_by_application_id(applications)
    return (
        jsonify(
            [
                _application_payload(a, placements_by_application_id)
                for a in applications
            ]
        ),
        200,
    )


@student_bp.route("/placement/confirmation", methods=["GET"])
@role_required("student")
def placement_confirmation():
    placement = Placement.query.filter_by(
        student_id=current_user.student_profile.id
    ).first()
    if placement is None:
        return jsonify({"error": "No placement on file"}), 404

    body = (
        "Placement Confirmation\n"
        "=======================\n\n"
        f"Student: {current_user.student_profile.name}\n"
        f"Position: {placement.position_title}\n"
        f"Salary: {placement.salary}\n"
        f"Joining Date: {placement.joining_date}\n"
    )
    return Response(
        body,
        mimetype="text/plain",
        headers={
            "Content-Disposition": "attachment; filename=placement_confirmation.txt"
        },
    )
