from flask import Blueprint, jsonify
from flask_login import current_user

from app.decorators import role_required

company_bp = Blueprint("company", __name__, url_prefix="/api/company")


@company_bp.route("/ping", methods=["GET"])
@role_required("company")
def ping():
    # Always responds, even while pending - only company-only *capabilities*
    # (added from Milestone 4 onward) are gated on approval_status, not login itself.
    return jsonify(
        {
            "message": f"Hello, {current_user.username} (company)",
            "approval_status": current_user.company_profile.approval_status,
        }
    ), 200
