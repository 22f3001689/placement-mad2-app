from flask import Blueprint, jsonify
from flask_login import current_user

from app.decorators import role_required

student_bp = Blueprint("student", __name__, url_prefix="/api/student")


@student_bp.route("/ping", methods=["GET"])
@role_required("student")
def ping():
    return jsonify({"message": f"Hello, {current_user.username} (student)"}), 200
