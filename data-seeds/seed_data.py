from datetime import datetime, timedelta

from app import create_app, db
from app.models import (
    Application,
    Branch,
    Company,
    JobPosition,
    Placement,
    Skill,
    Student,
    User,
)

BRANCHES = [
    ("CSE", "Computer Science and Engineering", "Software, algorithms, and systems design."),
    ("ME", "Mechanical Engineering", "Design, manufacturing, and mechanical systems."),
    ("EE", "Electrical Engineering", "Power systems, circuits, and electrical machines."),
    ("DS", "Data Science", "Statistics, machine learning, and data analytics."),
    ("ECE", "Electronics and Communication Engineering", "Electronics, signals, and communication systems."),
]

SKILLS = [
    "Python",
    "Java",
    "SQL",
    "Flask",
    "JavaScript",
    "Machine Learning",
    "Data Analysis",
    "Communication",
]


def seed_database():
    app = create_app()
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Creating branches...")
        branches = {}
        for code, name, description in BRANCHES:
            branch = Branch(code=code, name=name, description=description)
            db.session.add(branch)
            branches[code] = branch
        db.session.commit()

        print("Creating skills...")
        skills = {}
        for name in SKILLS:
            skill = Skill(name=name)
            db.session.add(skill)
            skills[name] = skill
        db.session.commit()

        print("Creating admin...")
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)

        print("Creating a sample company...")
        company_user = User(username="acme_corp", role="company")
        company_user.set_password("company123")
        db.session.add(company_user)
        db.session.commit()

        company = Company(
            user_id=company_user.id,
            company_name="Acme Corp",
            industry="Software",
            location="Bangalore",
            hr_contact="hr@acme.example",
            website="https://acme.example",
            logo_path="uploads/logos/acme_corp.png",
            overview=(
                "Through the application of innovation and our contextual knowledge, we give "
                "associates the opportunity to deliver transformative outcomes that benefit "
                "society at large and prove that anything is possible."
            ),
            approval_status="approved",
        )
        db.session.add(company)

        print("Creating a sample student...")
        student_user = User(username="john_doe", role="student")
        student_user.set_password("student123")
        db.session.add(student_user)
        db.session.commit()

        student = Student(
            user_id=student_user.id,
            name="John Doe",
            branch_id=branches["CSE"].id,
            graduation_year=2026,
            cgpa=8.5,
            resume_path="uploads/resumes/john_doe.pdf",
            photo_path="uploads/photos/john_doe.png",
            contact="john.doe@example.com",
        )
        student.skills = [skills["Python"], skills["Flask"], skills["SQL"]]
        db.session.add(student)
        db.session.commit()

        print("Creating a sample job position and application...")
        job_position = JobPosition(
            company_id=company.id,
            drive_name="Drive 1",
            title="Software Engineer",
            description="Entry-level backend role.",
            eligibility_criteria="B.Tech Computer Science, CGPA >= 7.0, 2026 batch",
            salary=800000,
            skills_required="Python, SQL",
            location="Bangalore",
            application_deadline=datetime.utcnow() + timedelta(days=30),
            status="ongoing",
        )
        db.session.add(job_position)
        db.session.commit()

        application = Application(
            student_id=student.id,
            job_position_id=job_position.id,
            status="selected",
        )
        db.session.add(application)
        db.session.commit()

        print("Creating the resulting placement...")
        placement = Placement(
            student_id=student.id,
            company_id=company.id,
            application_id=application.id,
            position_title=job_position.title,
            salary=job_position.salary,
            joining_date=datetime.utcnow().date() + timedelta(days=60),
        )
        db.session.add(placement)
        db.session.commit()

        print("\nDatabase seeded successfully!")
        print("\nLogin Credentials:")
        print("Admin: admin / admin123")
        print("Company: acme_corp / company123")
        print("Student: john_doe / student123")


if __name__ == "__main__":
    seed_database()
