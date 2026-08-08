from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from app import db
from app.constants import (
    COMPANY_APPROVAL_APPROVED,
    COMPANY_DECISION_STATUSES,
    JOB_POSITION_STATUS_COMPLETED,
)
from app.decorators import role_required
from app.models import Application, Company, JobPosition, Student, User
from app.utils import branch_payload, placement_payloads_by_application_id, static_url

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _company_payload(company):
    return {
        "id": company.id,
        "user_id": company.user_id,
        "username": company.user.username,
        "company_name": company.company_name,
        "industry": company.industry,
        "approval_status": company.approval_status,
        "is_active": company.user.is_active,
        "logo_url": static_url(company.logo_path),
    }


def _student_payload(student):
    return {
        "id": student.id,
        "user_id": student.user_id,
        "username": student.user.username,
        "name": student.name,
        "contact": student.contact,
        "is_active": student.user.is_active,
        "photo_url": static_url(student.photo_path),
        "resume_url": static_url(student.resume_path),
    }


def _job_position_payload(job_position):
    return {
        "id": job_position.id,
        "drive_name": job_position.drive_name,
        "title": job_position.title,
        "description": job_position.description,
        "company_name": job_position.company.company_name,
        "company_logo_url": static_url(job_position.company.logo_path),
        "location": job_position.location,
        "eligibility_criteria": job_position.eligibility_criteria,
        "salary": job_position.salary,
        "skills_required": job_position.skills_required,
        "status": job_position.status,
        "application_deadline": job_position.application_deadline.isoformat(),
    }


def _application_payload(application):
    return {
        "id": application.id,
        "student_name": application.student.name,
        "student_photo_url": static_url(application.student.photo_path),
        "student_resume_url": static_url(application.student.resume_path),
        "job_title": application.job_position.title,
        "company_name": application.job_position.company.company_name,
        "status": application.status,
        "application_date": application.application_date.isoformat(),
    }


def _application_history_payload(application, placements_by_application_id):
    return {
        "id": application.id,
        "job_title": application.job_position.title,
        "company_name": application.job_position.company.company_name,
        "status": application.status,
        "application_date": application.application_date.isoformat(),
        "interview_datetime": (
            application.interview_datetime.isoformat()
            if application.interview_datetime
            else None
        ),
        "interview_mode": application.interview_mode,
        "company_remark": application.company_remark,
        "placement": placements_by_application_id.get(application.id),
    }


def _student_detail_payload(student):
    placements_by_application_id = placement_payloads_by_application_id(
        student.applications
    )
    return {
        "id": student.id,
        "user_id": student.user_id,
        "username": student.user.username,
        "is_active": student.user.is_active,
        "name": student.name,
        "branch": branch_payload(student.branch) if student.branch else None,
        "graduation_year": student.graduation_year,
        "cgpa": student.cgpa,
        "skills": [{"id": s.id, "name": s.name} for s in student.skills],
        "contact": student.contact,
        "photo_url": static_url(student.photo_path),
        "resume_url": static_url(student.resume_path),
        "applications": [
            _application_history_payload(a, placements_by_application_id)
            for a in student.applications
        ],
    }


@admin_bp.route("/dashboard", methods=["GET"])
@role_required("admin")
def dashboard():
    return (
        jsonify(
            {
                "students": Student.query.count(),
                "companies": Company.query.filter_by(
                    approval_status=COMPANY_APPROVAL_APPROVED
                ).count(),
                "job_positions": JobPosition.query.count(),
                "applications": Application.query.count(),
            }
        ),
        200,
    )


@admin_bp.route("/companies", methods=["GET"])
@role_required("admin")
def list_companies():
    query = Company.query.join(User, Company.user_id == User.id)

    status = request.args.get("status")
    if status:
        query = query.filter(Company.approval_status == status)

    q = request.args.get("q")
    if q:
        query = query.filter(
            or_(Company.company_name.ilike(f"%{q}%"), Company.industry.ilike(f"%{q}%"))
        )

    return jsonify([_company_payload(c) for c in query.all()]), 200


@admin_bp.route("/companies/<int:company_id>/decision", methods=["POST"])
@role_required("admin")
def decide_company(company_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in COMPANY_DECISION_STATUSES:
        return jsonify({"error": "status must be 'approved' or 'rejected'"}), 400

    company = Company.query.get(company_id)
    if company is None:
        return jsonify({"error": "Company not found"}), 404

    company.approval_status = status
    db.session.commit()
    return jsonify({"id": company.id, "approval_status": company.approval_status}), 200


@admin_bp.route("/students", methods=["GET"])
@role_required("admin")
def list_students():
    query = Student.query.join(User, Student.user_id == User.id)

    q = request.args.get("q")
    if q:
        query = query.filter(
            or_(
                Student.name.ilike(f"%{q}%"),
                User.username.ilike(f"%{q}%"),
                Student.contact.ilike(f"%{q}%"),
            )
        )

    return jsonify([_student_payload(s) for s in query.all()]), 200


@admin_bp.route("/students/<int:student_id>", methods=["GET"])
@role_required("admin")
def get_student(student_id):
    student = Student.query.get(student_id)
    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(_student_detail_payload(student)), 200


@admin_bp.route("/job-positions", methods=["GET"])
@role_required("admin")
def list_job_positions():
    query = JobPosition.query

    status = request.args.get("status")
    if status:
        query = query.filter(JobPosition.status == status)

    return jsonify([_job_position_payload(jp) for jp in query.all()]), 200


@admin_bp.route("/job-positions/<int:job_position_id>/complete", methods=["POST"])
@role_required("admin")
def complete_job_position(job_position_id):
    job_position = JobPosition.query.get(job_position_id)
    if job_position is None:
        return jsonify({"error": "Job Posting not found"}), 404

    job_position.status = JOB_POSITION_STATUS_COMPLETED
    db.session.commit()
    return jsonify({"id": job_position.id, "status": job_position.status}), 200


@admin_bp.route("/applications", methods=["GET"])
@role_required("admin")
def list_applications():
    applications = Application.query.all()
    return jsonify([_application_payload(a) for a in applications]), 200


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@role_required("admin")
def toggle_active(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    if user.role == "admin":
        return jsonify({"error": "Cannot deactivate the Admin account"}), 403

    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({"id": user.id, "is_active": user.is_active}), 200
