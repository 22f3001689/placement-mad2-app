from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login
from app.constants import (
    APPLICATION_STATUS_APPLIED,
    COMPANY_APPROVAL_APPROVED,
    COMPANY_APPROVAL_PENDING,
    EXPORT_JOB_STATUS_PENDING,
    JOB_POSITION_STATUS_ONGOING,
)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
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
    logo_path = db.Column(db.String(255), nullable=True)
    overview = db.Column(db.Text, nullable=True)
    approval_status = db.Column(
        db.String(20), nullable=False, default=COMPANY_APPROVAL_PENDING
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("company_profile", uselist=False))

    @hybrid_property
    def is_visible_to_students(self):
        """Approved and not blacklisted - the single gate for student-facing visibility."""
        return self.approval_status == COMPANY_APPROVAL_APPROVED and self.user.is_active

    @is_visible_to_students.expression
    def is_visible_to_students(cls):
        return db.and_(
            cls.approval_status == COMPANY_APPROVAL_APPROVED,
            cls.user.has(is_active=True),
        )

    def __repr__(self):
        return f"<Company {self.company_name}>"


class Branch(db.Model):
    """Seeded list of Student branches (CSE, ME, ...) - not user-editable."""

    __tablename__ = "branch"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Branch {self.code}>"


class Skill(db.Model):
    """Skills a Student or Drive can be tagged with, picked from this fixed list."""

    __tablename__ = "skill"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Skill {self.name}>"


student_skill = db.Table(
    "student_skill",
    db.Column("student_id", db.Integer, db.ForeignKey("student.id"), primary_key=True),
    db.Column("skill_id", db.Integer, db.ForeignKey("skill.id"), primary_key=True),
)


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    resume_path = db.Column(db.String(255), nullable=True)
    photo_path = db.Column(db.String(255), nullable=True)
    contact = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("student_profile", uselist=False))
    branch = db.relationship("Branch")
    skills = db.relationship("Skill", secondary=student_skill, backref="students")

    def __repr__(self):
        return f"<Student {self.name}>"


job_position_skill = db.Table(
    "job_position_skill",
    db.Column(
        "job_position_id",
        db.Integer,
        db.ForeignKey("job_position.id"),
        primary_key=True,
    ),
    db.Column("skill_id", db.Integer, db.ForeignKey("skill.id"), primary_key=True),
)


class JobPosition(db.Model):
    """A recruitment opening posted by a Company. Also referred to as a Placement Drive."""

    __tablename__ = "job_position"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    drive_name = db.Column(db.String(150), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.Text, nullable=True)
    salary = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(150), nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default=JOB_POSITION_STATUS_ONGOING
    )
    closed_by_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship(
        "Company",
        backref=db.backref("job_positions", cascade="all, delete-orphan"),
    )
    skills = db.relationship(
        "Skill", secondary=job_position_skill, backref="job_positions"
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
    status = db.Column(
        db.String(20), nullable=False, default=APPLICATION_STATUS_APPLIED
    )
    interview_datetime = db.Column(db.DateTime, nullable=True)
    interview_mode = db.Column(db.String(20), nullable=True)
    interview_reminded_at = db.Column(db.DateTime, nullable=True)
    company_remark = db.Column(db.Text, nullable=True)

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

    Not cascaded from Company/JobPosition/Application - it's a snapshot that has to
    keep reading correctly even after the company is deactivated or the drive closed.
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


class EmailTemplate(db.Model):
    """Seeded, reusable email subject/body with str.format() placeholders.

    Not user-editable via any UI in this milestone - a fixed set, like Branch/Skill.
    """

    __tablename__ = "email_template"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<EmailTemplate {self.key}>"


class ExportJob(db.Model):
    """One asynchronous background-job request: a user-triggered CSV export or a
    system-generated placement report. Both share the same status/file-path shape,
    discriminated by job_type (see app/constants.py).

    For a placement_report, user_id is the owning Company's user_id - a Company IS
    a User via Company.user_id, so ownership/visibility reuses the same "is this
    job's user_id mine" check as an export.
    """

    __tablename__ = "export_job"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=EXPORT_JOB_STATUS_PENDING)
    file_path = db.Column(db.String(255), nullable=True)
    period_start = db.Column(db.Date, nullable=True)
    period_end = db.Column(db.Date, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref="export_jobs")

    def __repr__(self):
        return f"<ExportJob {self.job_type} user={self.user_id} status={self.status}>"


@login.user_loader
def load_user(uid):
    """Loads a user from the database (used by Flask-Login)."""
    return User.query.get(int(uid))
