from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models import Company, Student, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _user_payload(user):
    payload = {"username": user.username, "role": user.role}
    if user.role == "company":
        payload["approval_status"] = user.company_profile.approval_status
    return payload


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    name = data.get("name")

    if not all([username, password, name]):
        return jsonify({"error": "username, password and name are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    user = User(username=username, role="student")
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    student = Student(user_id=user.id, name=name)
    db.session.add(student)
    db.session.commit()

    return jsonify(_user_payload(user)), 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    company_name = data.get("company_name")

    if not all([username, password, company_name]):
        return jsonify({"error": "username, password and company_name are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    user = User(username=username, role="company")
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    company = Company(user_id=user.id, company_name=company_name)
    db.session.add(company)
    db.session.commit()

    return jsonify(_user_payload(user)), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401
    if not user.is_active:
        return jsonify({"error": "This account has been deactivated"}), 403

    login_user(user)
    return jsonify(_user_payload(user)), 200


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify(_user_payload(current_user)), 200
