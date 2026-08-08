from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.constants import ROLE_COMPANY, ROLE_STUDENT
from app.models import Branch, Company, Skill, Student, User
from app.utils import branch_payload, get_logger

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

logger = get_logger(__name__)


@auth_bp.route("/branches", methods=["GET"])
def list_branches():
    """Public - needed on the registration form, before any session exists."""
    branches = Branch.query.all()
    return jsonify([branch_payload(b) for b in branches]), 200


@auth_bp.route("/skills", methods=["GET"])
def list_skills():
    """Public - needed on the registration/profile form, before or regardless of session."""
    skills = Skill.query.all()
    return jsonify([{"id": s.id, "name": s.name} for s in skills]), 200


def _user_payload(user):
    payload = {"username": user.username, "role": user.role}
    if user.role == ROLE_COMPANY:
        payload["approval_status"] = user.company_profile.approval_status
        payload["company_name"] = user.company_profile.company_name
    return payload


def _registration_error(username, password, email):
    """The username/password/email checks shared verbatim by both registration routes.

    Returns (error_message, status_code), or (None, None) if all pass.
    """
    if len(password) < 6:
        return "Password must be at least 6 characters long", 400
    if "@" not in email:
        return "email must be a valid email address", 400
    if User.query.filter_by(username=username).first():
        return "Username already exists", 409
    if User.query.filter_by(email=email).first():
        return "Email already registered", 409
    return None, None


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    name = data.get("name")
    branch_id = data.get("branch_id")

    if not all([username, password, email, name]):
        return (
            jsonify({"error": "username, password, email and name are required"}),
            400,
        )
    error, status = _registration_error(username, password, email)
    if error:
        return jsonify({"error": error}), status
    if branch_id is not None and Branch.query.get(branch_id) is None:
        return jsonify({"error": "branch_id must be a valid Branch"}), 400

    user = User(username=username, email=email, role=ROLE_STUDENT)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    student = Student(user_id=user.id, name=name, branch_id=branch_id)
    db.session.add(student)
    db.session.commit()

    logger.info("Student registered: user_id=%s username=%s", user.id, username)
    return jsonify(_user_payload(user)), 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    company_name = data.get("company_name")

    if not all([username, password, email, company_name]):
        return (
            jsonify(
                {"error": "username, password, email and company_name are required"}
            ),
            400,
        )
    error, status = _registration_error(username, password, email)
    if error:
        return jsonify({"error": error}), status

    user = User(username=username, email=email, role=ROLE_COMPANY)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    company = Company(user_id=user.id, company_name=company_name)
    db.session.add(company)
    db.session.commit()

    logger.info("Company registered: user_id=%s username=%s", user.id, username)
    return jsonify(_user_payload(user)), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        logger.warning("Login failed: username=%s (invalid credentials)", username)
        return jsonify({"error": "Invalid username or password"}), 401
    if not user.is_active:
        logger.warning(
            "Login blocked: user_id=%s username=%s (deactivated)", user.id, username
        )
        return jsonify({"error": "This account has been deactivated"}), 403

    login_user(user)
    logger.info(
        "Login succeeded: user_id=%s username=%s role=%s", user.id, username, user.role
    )
    return jsonify(_user_payload(user)), 200


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logger.info(
        "Logout: user_id=%s username=%s", current_user.id, current_user.username
    )
    logout_user()
    return jsonify({"message": "Logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify(_user_payload(current_user)), 200
