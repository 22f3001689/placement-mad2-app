from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def role_required(*roles):
    """Require an active login AND one of the given roles, in that order.

    401 (via login_required) if there's no session at all; 403 if there is one
    but it's the wrong role for this endpoint.
    """

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator
