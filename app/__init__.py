from flask import Flask, abort, jsonify, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
login = LoginManager()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)

    @login.unauthorized_handler
    def unauthorized():
        # This is a JSON API, not a Jinja app - no login page to redirect to.
        return jsonify({"error": "Not logged in"}), 401

    @app.errorhandler(403)
    def forbidden(_e):
        return jsonify({"error": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Not found"}), 404

    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.company import company_bp
    from app.routes.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    @app.route("/")
    @app.route("/<path:path>")
    def serve_frontend(path=None):
        # Single Jinja entry-point shell that bootstraps the Vue SPA - Vue Router
        # handles everything past this, so any non-/api path lands here. A path
        # under /api that didn't match a real route is a genuine 404, not a page.
        if path and path.startswith("api/"):
            abort(404)
        return render_template("index.html")

    return app
