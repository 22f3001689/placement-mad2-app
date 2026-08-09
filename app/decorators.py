from functools import wraps

from flask import abort, jsonify
from flask_login import current_user, login_required

from app.constants import COMPANY_APPROVAL_APPROVED, ROLE_COMPANY
from app.utils import get_logger

logger = get_logger(__name__)


def role_required(*roles):
    """401 if not logged in, 403 if logged in as the wrong role."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logger.warning(
                    "Access denied: user_id=%s role=%s attempted %s (requires %s)",
                    current_user.id,
                    current_user.role,
                    view.__name__,
                    roles,
                )
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def company_approved_required(view):
    """Same as role_required(ROLE_COMPANY), plus a 403 if not yet approved."""

    @wraps(view)
    @role_required(ROLE_COMPANY)
    def wrapped(*args, **kwargs):
        if current_user.company_profile.approval_status != COMPANY_APPROVAL_APPROVED:
            logger.warning(
                "Access denied: company_id=%s (user_id=%s) not approved, attempted %s",
                current_user.company_profile.id,
                current_user.id,
                view.__name__,
            )
            return jsonify({"error": "Company is not yet approved"}), 403
        return view(*args, **kwargs)

    return wrapped
