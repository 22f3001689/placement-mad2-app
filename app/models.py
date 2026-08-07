from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / company / student
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    company_name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(150), nullable=True)
    hr_contact = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    approval_status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship(
        "User", backref=db.backref("company_profile", uselist=False)
    )

    def __repr__(self):
        return f"<Company {self.company_name}>"


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(100), nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    resume_path = db.Column(db.String(255), nullable=True)
    contact = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship(
        "User", backref=db.backref("student_profile", uselist=False)
    )

    def __repr__(self):
        return f"<Student {self.name}>"


class JobPosition(db.Model):
    """A recruitment opening posted by a Company. Also referred to as a Placement Drive."""

    __tablename__ = "job_position"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    eligible_branches = db.Column(db.String(255), nullable=True)
    min_cgpa = db.Column(db.Float, nullable=True)
    eligible_graduation_year = db.Column(db.Integer, nullable=True)
    salary = db.Column(db.Integer, nullable=True)
    skills_required = db.Column(db.Text, nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship(
        "Company",
        backref=db.backref("job_positions", cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<JobPosition {self.title}>"


class Application(db.Model):
    """A Student's application to one JobPosition."""

    __tablename__ = "application"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    job_position_id = db.Column(
        db.Integer, db.ForeignKey("job_position.id"), nullable=False
    )
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="applied")

    student = db.relationship(
        "Student",
        backref=db.backref("applications", cascade="all, delete-orphan"),
    )
    # No cascade here: closing/removing a JobPosition must not erase Application history.
    job_position = db.relationship("JobPosition", backref="applications")

    # One Student can only apply once to a given Job Position.
    __table_args__ = (
        db.UniqueConstraint("student_id", "job_position_id", name="_student_job_uc"),
    )

    def __repr__(self):
        return f"<Application student={self.student_id} job_position={self.job_position_id}>"


class Placement(db.Model):
    """The final, durable placement outcome for a Student.

    Deliberately not cascaded from Company/JobPosition/Application - a Placement is a
    snapshot that must keep reading correctly even if the company is deactivated or the
    job position is later closed (see spec.md edge cases).
    """

    __tablename__ = "placement"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    application_id = db.Column(
        db.Integer, db.ForeignKey("application.id"), unique=True, nullable=True
    )
    position_title = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.Integer, nullable=True)
    joining_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="placements")

    def __repr__(self):
        return f"<Placement student={self.student_id} company={self.company_id}>"


@login.user_loader
def load_user(uid):
    """Loads a user from the database (used by Flask-Login)."""
    return User.query.get(int(uid))
