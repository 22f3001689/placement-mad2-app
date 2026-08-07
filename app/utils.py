from flask import url_for


def static_url(path):
    """Builds a URL for a file under app/static/, or None if path is falsy."""
    return url_for("static", filename=path) if path else None
