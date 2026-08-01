from flask import Blueprint, jsonify
from flask_login import current_user

from app.decorators import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/ping", methods=["GET"])
@role_required("admin")
def ping():
    return jsonify({"message": f"Hello, {current_user.username} (admin)"}), 200
