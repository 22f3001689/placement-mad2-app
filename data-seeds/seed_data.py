import os
import struct
import zlib
from datetime import datetime, timedelta

from app import create_app, db
from app.cache import invalidate
from app.models import (
    Application,
    Branch,
    Company,
    EmailTemplate,
    JobPosition,
    Placement,
    Skill,
    Student,
    User,
)

BRANCHES = [
    (
        "CSE",
        "Computer Science and Engineering",
        "Software, algorithms, and systems design.",
    ),
    ("ME", "Mechanical Engineering", "Design, manufacturing, and mechanical systems."),
    (
        "EE",
        "Electrical Engineering",
        "Power systems, circuits, and electrical machines.",
    ),
    ("DS", "Data Science", "Statistics, machine learning, and data analytics."),
    (
        "ECE",
        "Electronics and Communication Engineering",
        "Electronics, signals, and communication systems.",
    ),
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

EMAIL_TEMPLATES = [
    (
        "interview_reminder",
        "Interview Reminder: {job_title} at {company_name}",
        (
            "Hi {student_name},\n\n"
            "This is a reminder that you have an interview for {job_title} at "
            "{company_name} on {interview_datetime}.\n\nGood luck!"
        ),
    ),
    (
        "export_ready",
        "Your export is ready",
        "Hi {name},\n\nYour requested export is ready to download:\n{download_url}",
    ),
    (
        "report_ready",
        "Placement report ready for {company_name}",
        (
            "Hi,\n\nA new placement report for {company_name} covering "
            "{period_start} to {period_end} is ready to download:\n{download_url}"
        ),
    ),
]

# 29 additional students (index 0, "John Doe", is created separately below to keep
# the long-standing john_doe/student123 demo login working). Indian names, mixed
# regions, so search/report demos have real variety to filter/sort on.
STUDENT_NAMES = [
    ("Aarav", "Sharma"),
    ("Vivaan", "Mehta"),
    ("Aditya", "Verma"),
    ("Vihaan", "Gupta"),
    ("Arjun", "Nair"),
    ("Sai", "Reddy"),
    ("Ishaan", "Patel"),
    ("Krishna", "Iyer"),
    ("Rohan", "Malhotra"),
    ("Karthik", "Rao"),
    ("Ananya", "Singh"),
    ("Diya", "Kapoor"),
    ("Saanvi", "Joshi"),
    ("Aadhya", "Pillai"),
    ("Myra", "Chatterjee"),
    ("Kiara", "Bansal"),
    ("Riya", "Desai"),
    ("Anika", "Menon"),
    ("Navya", "Bhat"),
    ("Pihu", "Agarwal"),
    ("Aryan", "Choudhary"),
    ("Kabir", "Khanna"),
    ("Yash", "Trivedi"),
    ("Dhruv", "Saxena"),
    ("Om", "Bhatt"),
    ("Advait", "Kulkarni"),
    ("Reyansh", "Chauhan"),
    ("Shaurya", "Dubey"),
    ("Aarohi", "Mishra"),
]

# A few solid, demo-friendly colors, cycled per student - avoids pulling in an
# image library or fetching real photos over the network for a local-demo app.
AVATAR_COLORS = [
    (244, 67, 54),
    (33, 150, 243),
    (76, 175, 80),
    (255, 152, 0),
    (156, 39, 176),
    (0, 150, 136),
    (233, 30, 99),
    (63, 81, 181),
    (255, 193, 7),
    (0, 188, 212),
]


def _write_solid_png(path, color, size=128):
    """Writes a minimal solid-color PNG - a placeholder avatar with no dependency
    on Pillow or any network fetch (see AVATAR_COLORS above)."""

    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data))
        )

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    row = b"\x00" + bytes(color) * size
    idat = chunk(b"IDAT", zlib.compress(row * size))
    iend = chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(signature + ihdr + idat + iend)


def seed_database():
    app = create_app()
    with app.app_context():
        now = datetime.utcnow()

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
        branch_codes = list(branches.keys())

        print("Creating skills...")
        skills = {}
        for name in SKILLS:
            skill = Skill(name=name)
            db.session.add(skill)
            skills[name] = skill
        db.session.commit()

        print("Creating email templates...")
        for key, subject, body in EMAIL_TEMPLATES:
            db.session.add(EmailTemplate(key=key, subject=subject, body=body))
        db.session.commit()

        print("Creating admin...")
        admin = User(
            username="admin", email="admin@placement-portal.example", role="admin"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

        print("Creating companies...")
        photos_dir = os.path.join(app.static_folder, "uploads", "photos")
        os.makedirs(photos_dir, exist_ok=True)

        company_specs = [
            (
                "acme_corp",
                "hr@acme.example",
                "Acme Corp",
                "Software",
                "Bangalore",
                "hr@acme.example",
                "https://acme.example",
                "uploads/logos/acme_corp.png",
                (
                    "Through the application of innovation and our contextual knowledge, we give "
                    "associates the opportunity to deliver transformative outcomes that benefit "
                    "society at large and prove that anything is possible."
                ),
                90,
            ),
            (
                "nimbus_cloud",
                "careers@nimbuscloud.example",
                "Nimbus Cloud Technologies",
                "Cloud Infrastructure",
                "Hyderabad",
                "careers@nimbuscloud.example",
                "https://nimbuscloud.example",
                None,
                "We build the cloud platforms other companies build their products on - reliable, scalable, and boring in the best way.",
                75,
            ),
            (
                "bharat_motors",
                "careers@bharatmotors.example",
                "Bharat Motors Ltd",
                "Automotive",
                "Pune",
                "careers@bharatmotors.example",
                "https://bharatmotors.example",
                None,
                "A century-old name in Indian manufacturing, now building the next generation of electric commercial vehicles.",
                60,
            ),
            (
                "quantix_analytics",
                "careers@quantix.example",
                "Quantix Analytics",
                "Data Analytics",
                "Chennai",
                "careers@quantix.example",
                "https://quantix.example",
                None,
                "We turn messy data into decisions for retail and logistics clients across South Asia.",
                45,
            ),
        ]

        companies = {}
        for (
            username,
            email,
            company_name,
            industry,
            location,
            hr_contact,
            website,
            logo_path,
            overview,
            created_days_ago,
        ) in company_specs:
            user = User(username=username, email=email, role="company")
            user.set_password("company123")
            db.session.add(user)
            db.session.commit()

            company = Company(
                user_id=user.id,
                company_name=company_name,
                industry=industry,
                location=location,
                hr_contact=hr_contact,
                website=website,
                logo_path=logo_path,
                overview=overview,
                approval_status="approved",
                created_at=now - timedelta(days=created_days_ago),
            )
            db.session.add(company)
            db.session.commit()
            companies[username] = company

        print("Creating students...")
        students = []

        john_user = User(
            username="john_doe", email="john.doe@example.com", role="student"
        )
        john_user.set_password("student123")
        db.session.add(john_user)
        db.session.commit()
        john = Student(
            user_id=john_user.id,
            name="John Doe",
            branch_id=branches["CSE"].id,
            graduation_year=2026,
            cgpa=8.5,
            resume_path="uploads/resumes/john_doe.pdf",
            photo_path="uploads/photos/john_doe.png",
            contact="+91-9800000000",
        )
        john.skills = [skills["Python"], skills["Flask"], skills["SQL"]]
        db.session.add(john)
        db.session.commit()
        students.append(john)

        for i, (first, last) in enumerate(STUDENT_NAMES):
            username = f"{first.lower()}.{last.lower()}"
            email = f"{username}@example.com"
            user = User(username=username, email=email, role="student")
            user.set_password("student123")
            db.session.add(user)
            db.session.commit()

            photo_filename = f"{username}.png"
            _write_solid_png(
                os.path.join(photos_dir, photo_filename),
                AVATAR_COLORS[i % len(AVATAR_COLORS)],
            )

            student = Student(
                user_id=user.id,
                name=f"{first} {last}",
                branch_id=branches[branch_codes[i % len(branch_codes)]].id,
                graduation_year=2025 + (i % 3),
                cgpa=round(6.5 + (i % 30) * 0.1, 2),
                photo_path=f"uploads/photos/{photo_filename}",
                contact=f"+91-9{800000000 + i * 7 % 100000000:08d}",
            )
            student.skills = [
                skills[SKILLS[i % len(SKILLS)]],
                skills[SKILLS[(i + 3) % len(SKILLS)]],
                skills[SKILLS[(i + 5) % len(SKILLS)]],
            ]
            db.session.add(student)
            db.session.commit()
            students.append(student)

        print("Creating drives (some closed with historical outcomes, some ongoing)...")

        def make_drive(
            company_key,
            drive_name,
            title,
            description,
            eligibility,
            salary,
            location,
            skill_names,
            days_offset,
            status,
        ):
            deadline = now + timedelta(days=days_offset)
            drive = JobPosition(
                company_id=companies[company_key].id,
                drive_name=drive_name,
                title=title,
                description=description,
                eligibility_criteria=eligibility,
                salary=salary,
                location=location,
                skills=[skills[name] for name in skill_names],
                application_deadline=deadline,
                status=status,
            )
            db.session.add(drive)
            db.session.commit()
            return drive, deadline

        closed_backend, deadline_backend = make_drive(
            "acme_corp",
            "Acme Backend Drive 2025",
            "Backend Developer",
            "Own backend services powering Acme's core product.",
            "B.Tech CSE/IT, CGPA >= 7.0",
            900000,
            "Bangalore",
            ["Python", "SQL", "Flask"],
            -50,
            "completed",
        )
        closed_cloud, deadline_cloud = make_drive(
            "nimbus_cloud",
            "Nimbus Cloud Engineer Drive",
            "Cloud Engineer",
            "Design and operate multi-region cloud infrastructure.",
            "B.Tech CSE/ECE, CGPA >= 7.0",
            1100000,
            "Hyderabad",
            ["Python", "Communication"],
            -40,
            "completed",
        )
        closed_get, deadline_get = make_drive(
            "bharat_motors",
            "Bharat GET Drive 2025",
            "Graduate Engineer Trainee",
            "Rotational trainee program across manufacturing and design.",
            "B.Tech ME/EE, CGPA >= 6.5",
            600000,
            "Pune",
            ["Communication"],
            -35,
            "completed",
        )
        closed_analyst, deadline_analyst = make_drive(
            "quantix_analytics",
            "Quantix Data Analyst Drive",
            "Data Analyst",
            "Analyze retail transaction data to drive client recommendations.",
            "B.Tech/B.Sc any branch, CGPA >= 7.0",
            750000,
            "Chennai",
            ["SQL", "Data Analysis"],
            -20,
            "completed",
        )

        open_intern, _ = make_drive(
            "acme_corp",
            "Acme Summer Internship 2026",
            "Software Engineer Intern",
            "6-month internship building internal developer tools.",
            "B.Tech CSE/IT, 2026/2027 batch",
            400000,
            "Bangalore",
            ["Python", "JavaScript"],
            20,
            "ongoing",
        )
        open_devops, _ = make_drive(
            "nimbus_cloud",
            "Nimbus DevOps Hiring Drive",
            "DevOps Associate",
            "Automate deployment pipelines for our cloud platform.",
            "B.Tech CSE/ECE, CGPA >= 6.5",
            950000,
            "Hyderabad",
            ["Python", "Communication"],
            15,
            "ongoing",
        )
        open_mech, _ = make_drive(
            "bharat_motors",
            "Bharat Mechanical Design Drive",
            "Mechanical Design Engineer",
            "Design components for next-gen electric commercial vehicles.",
            "B.Tech ME, CGPA >= 7.0",
            850000,
            "Pune",
            ["Communication"],
            25,
            "ongoing",
        )
        open_ml, _ = make_drive(
            "quantix_analytics",
            "Quantix ML Engineer Drive",
            "Machine Learning Engineer",
            "Build forecasting models for logistics clients.",
            "B.Tech CSE/DS, CGPA >= 7.5",
            1300000,
            "Chennai",
            ["Python", "Machine Learning"],
            30,
            "ongoing",
        )

        def apply_and_decide(
            student, drive, deadline, status, offset_days=10, remark=None
        ):
            application = Application(
                student_id=student.id,
                job_position_id=drive.id,
                application_date=deadline - timedelta(days=offset_days),
                status=status,
                company_remark=remark,
            )
            db.session.add(application)
            db.session.commit()
            return application

        def place(
            student,
            company_key,
            drive,
            application,
            deadline,
            offset_days=1,
            joining_offset_days=30,
        ):
            placement = Placement(
                student_id=student.id,
                company_id=companies[company_key].id,
                application_id=application.id,
                position_title=drive.title,
                salary=drive.salary,
                joining_date=(deadline + timedelta(days=joining_offset_days)).date(),
                created_at=deadline - timedelta(days=offset_days),
            )
            db.session.add(placement)
            db.session.commit()

        print(
            "Filling closed drives with historical outcomes (placed/rejected/offer)..."
        )

        # Acme Backend Drive: John Doe + s[0..3] -> placed, placed, rejected, rejected, offer
        s = students
        a1 = apply_and_decide(s[0], closed_backend, deadline_backend, "placed", 10)
        place(s[0], "acme_corp", closed_backend, a1, deadline_backend, 2, 30)
        a2 = apply_and_decide(s[1], closed_backend, deadline_backend, "placed", 9)
        place(s[1], "acme_corp", closed_backend, a2, deadline_backend, 2, 30)
        apply_and_decide(
            s[2],
            closed_backend,
            deadline_backend,
            "rejected",
            8,
            "Did not meet system design bar.",
        )
        apply_and_decide(
            s[3],
            closed_backend,
            deadline_backend,
            "rejected",
            7,
            "Low CGPA relative to other candidates.",
        )
        apply_and_decide(s[4], closed_backend, deadline_backend, "offer", 6)

        # Nimbus Cloud Drive: s[5..9]
        a3 = apply_and_decide(s[5], closed_cloud, deadline_cloud, "placed", 10)
        place(s[5], "nimbus_cloud", closed_cloud, a3, deadline_cloud, 2, 30)
        a4 = apply_and_decide(s[6], closed_cloud, deadline_cloud, "placed", 9)
        place(s[6], "nimbus_cloud", closed_cloud, a4, deadline_cloud, 2, 30)
        apply_and_decide(
            s[7],
            closed_cloud,
            deadline_cloud,
            "rejected",
            8,
            "Weak on distributed systems fundamentals.",
        )
        apply_and_decide(s[8], closed_cloud, deadline_cloud, "rejected", 7)
        apply_and_decide(s[9], closed_cloud, deadline_cloud, "offer", 6)

        # Bharat GET Drive: s[10..13]
        a5 = apply_and_decide(s[10], closed_get, deadline_get, "placed", 10)
        place(s[10], "bharat_motors", closed_get, a5, deadline_get, 2, 45)
        apply_and_decide(s[11], closed_get, deadline_get, "rejected", 9)
        apply_and_decide(
            s[12],
            closed_get,
            deadline_get,
            "rejected",
            8,
            "Interview feedback: communication skills need work.",
        )
        apply_and_decide(s[13], closed_get, deadline_get, "offer", 7)

        # Quantix Data Analyst Drive: s[14..17]
        a6 = apply_and_decide(s[14], closed_analyst, deadline_analyst, "placed", 10)
        place(s[14], "quantix_analytics", closed_analyst, a6, deadline_analyst, 2, 20)
        a7 = apply_and_decide(s[15], closed_analyst, deadline_analyst, "placed", 9)
        place(s[15], "quantix_analytics", closed_analyst, a7, deadline_analyst, 2, 20)
        apply_and_decide(s[16], closed_analyst, deadline_analyst, "rejected", 8)
        apply_and_decide(s[17], closed_analyst, deadline_analyst, "offer", 7)

        print("Filling ongoing drives with in-progress applications...")

        # Acme Internship: s[18..21] - one scheduled interview ~2 minutes from now,
        # so the reminder job (or a manual trigger right after seeding) has
        # something real to remind about and send an email for, every time this
        # script runs.
        apply_and_decide(s[18], open_intern, now, "applied", offset_days=3)
        apply_and_decide(s[19], open_intern, now, "applied", offset_days=2)
        apply_and_decide(s[20], open_intern, now, "shortlisted", offset_days=4)
        interview_1 = apply_and_decide(
            s[21], open_intern, now, "interview", offset_days=5
        )
        interview_1.interview_datetime = now + timedelta(minutes=2)
        interview_1.interview_mode = "Video Call"
        db.session.commit()

        # Nimbus DevOps: s[22..24]
        apply_and_decide(s[22], open_devops, now, "applied", offset_days=2)
        apply_and_decide(s[23], open_devops, now, "shortlisted", offset_days=3)
        apply_and_decide(
            s[24],
            open_devops,
            now,
            "rejected",
            offset_days=4,
            remark="Not enough hands-on cloud experience yet.",
        )

        # Bharat Mechanical Design Drive: s[25..27] - a second, staggered interview
        apply_and_decide(s[25], open_mech, now, "applied", offset_days=2)
        interview_2 = apply_and_decide(
            s[26], open_mech, now, "interview", offset_days=3
        )
        interview_2.interview_datetime = now + timedelta(minutes=3)
        interview_2.interview_mode = "In-Person"
        db.session.commit()
        apply_and_decide(s[27], open_mech, now, "applied", offset_days=1)

        # Quantix ML Drive: s[28], s[0] (John Doe applying to a second, different drive)
        apply_and_decide(s[28], open_ml, now, "shortlisted", offset_days=2)
        apply_and_decide(s[0], open_ml, now, "applied", offset_days=1)

        print("Invalidating any pre-existing API cache entries...")
        for namespace in ("drives", "orgs", "admin_companies", "admin_students"):
            invalidate(namespace)

        print("\nDatabase seeded successfully!")
        print(f"  {len(students)} students, {len(companies)} companies, 8 drives")
        print("  4 closed drives with historical placed/rejected/offer outcomes")
        print(
            "  4 ongoing drives, including 2 interviews scheduled a couple minutes from now"
        )
        print("\nLogin Credentials:")
        print("Admin:   admin / admin123")
        print(
            "Company: acme_corp / company123  (also: nimbus_cloud, bharat_motors, quantix_analytics)"
        )
        print(
            "Student: john_doe / student123  (also: firstname.lastname / student123 for everyone else)"
        )


if __name__ == "__main__":
    seed_database()
