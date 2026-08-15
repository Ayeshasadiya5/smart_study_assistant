"""Seed engineering subjects and demo data."""
from app import create_app
from database.models import db, Subject, User

app = create_app()

# B.Tech Engineering subjects across all years and semesters
ENGINEERING_SUBJECTS = [
    # 1st Year - 1st Semester
    {'name': 'Engineering Mathematics I', 'subject_code': 'MA101', 'year': '1st Year', 'semester': '1st Semester',
     'description': 'Calculus, matrices, and differential equations'},
    {'name': 'Engineering Physics', 'subject_code': 'PH101', 'year': '1st Year', 'semester': '1st Semester',
     'description': 'Mechanics, waves, and thermodynamics'},
    {'name': 'Programming for Problem Solving', 'subject_code': 'CS101', 'year': '1st Year', 'semester': '1st Semester',
     'description': 'C programming and problem solving basics'},
    {'name': 'Engineering Chemistry', 'subject_code': 'CH101', 'year': '1st Year', 'semester': '1st Semester',
     'description': 'Chemistry fundamentals for engineers'},
    {'name': 'Professional Communication', 'subject_code': 'HS101', 'year': '1st Year', 'semester': '1st Semester',
     'description': 'Technical communication and soft skills'},

    # 1st Year - 2nd Semester
    {'name': 'Engineering Mathematics II', 'subject_code': 'MA102', 'year': '1st Year', 'semester': '2nd Semester',
     'description': 'Complex analysis, transforms, and numerical methods'},
    {'name': 'Basic Electrical Engineering', 'subject_code': 'EE102', 'year': '1st Year', 'semester': '2nd Semester',
     'description': 'Circuits, AC/DC, and electrical machines basics'},
    {'name': 'Engineering Drawing', 'subject_code': 'ME102', 'year': '1st Year', 'semester': '2nd Semester',
     'description': 'Technical drawing and CAD fundamentals'},
    {'name': 'Environmental Science', 'subject_code': 'EV102', 'year': '1st Year', 'semester': '2nd Semester',
     'description': 'Environment, sustainability, and ecology'},

    # 2nd Year - 1st Semester
    {'name': 'Data Structures', 'subject_code': 'CS201', 'year': '2nd Year', 'semester': '1st Semester',
     'description': 'Arrays, trees, graphs, and algorithm analysis'},
    {'name': 'Digital Logic Design', 'subject_code': 'EC201', 'year': '2nd Year', 'semester': '1st Semester',
     'description': 'Boolean algebra, combinational and sequential circuits'},
    {'name': 'Discrete Mathematics', 'subject_code': 'MA201', 'year': '2nd Year', 'semester': '1st Semester',
     'description': 'Logic, sets, relations, and graph theory'},
    {'name': 'Object Oriented Programming', 'subject_code': 'CS202', 'year': '2nd Year', 'semester': '1st Semester',
     'description': 'OOP concepts using Java/C++'},

    # 2nd Year - 2nd Semester
    {'name': 'Database Management Systems', 'subject_code': 'CS301', 'year': '2nd Year', 'semester': '2nd Semester',
     'description': 'SQL, normalization, and database design'},
    {'name': 'Operating Systems', 'subject_code': 'CS302', 'year': '2nd Year', 'semester': '2nd Semester',
     'description': 'Process management, memory, and file systems'},
    {'name': 'Design and Analysis of Algorithms', 'subject_code': 'CS303', 'year': '2nd Year', 'semester': '2nd Semester',
     'description': 'Algorithm design paradigms and complexity'},
    {'name': 'Computer Organization', 'subject_code': 'CS304', 'year': '2nd Year', 'semester': '2nd Semester',
     'description': 'CPU architecture, memory hierarchy, and I/O'},

    # 3rd Year - 1st Semester
    {'name': 'Computer Networks', 'subject_code': 'CS401', 'year': '3rd Year', 'semester': '1st Semester',
     'description': 'Networking protocols, TCP/IP, and network security'},
    {'name': 'Software Engineering', 'subject_code': 'CS402', 'year': '3rd Year', 'semester': '1st Semester',
     'description': 'SDLC, agile, testing, and project management'},
    {'name': 'Theory of Computation', 'subject_code': 'CS403', 'year': '3rd Year', 'semester': '1st Semester',
     'description': 'Automata, formal languages, and computability'},
    {'name': 'Microprocessors', 'subject_code': 'EC401', 'year': '3rd Year', 'semester': '1st Semester',
     'description': '8086 architecture, assembly, and interfacing'},

    # 3rd Year - 2nd Semester
    {'name': 'Web Technologies', 'subject_code': 'CS404', 'year': '3rd Year', 'semester': '2nd Semester',
     'description': 'HTML, CSS, JavaScript, and web frameworks'},
    {'name': 'Compiler Design', 'subject_code': 'CS405', 'year': '3rd Year', 'semester': '2nd Semester',
     'description': 'Lexical analysis, parsing, and code generation'},
    {'name': 'Information Security', 'subject_code': 'CS406', 'year': '3rd Year', 'semester': '2nd Semester',
     'description': 'Cryptography, network security, and ethical hacking'},
    {'name': 'Machine Learning', 'subject_code': 'CS407', 'year': '3rd Year', 'semester': '2nd Semester',
     'description': 'Supervised and unsupervised learning fundamentals'},

    # 4th Year - 1st Semester
    {'name': 'Artificial Intelligence', 'subject_code': 'CS501', 'year': '4th Year', 'semester': '1st Semester',
     'description': 'Search, knowledge representation, and expert systems'},
    {'name': 'Cloud Computing', 'subject_code': 'CS502', 'year': '4th Year', 'semester': '1st Semester',
     'description': 'Cloud models, virtualization, and AWS/Azure basics'},
    {'name': 'Deep Learning', 'subject_code': 'CS503', 'year': '4th Year', 'semester': '1st Semester',
     'description': 'Neural networks, CNNs, and RNNs'},
    {'name': 'Internet of Things', 'subject_code': 'CS504', 'year': '4th Year', 'semester': '1st Semester',
     'description': 'IoT architecture, sensors, and embedded systems'},

    # 4th Year - 2nd Semester
    {'name': 'Big Data Analytics', 'subject_code': 'CS505', 'year': '4th Year', 'semester': '2nd Semester',
     'description': 'Hadoop, Spark, and data analytics pipelines'},
    {'name': 'Blockchain Technology', 'subject_code': 'CS506', 'year': '4th Year', 'semester': '2nd Semester',
     'description': 'Distributed ledger, smart contracts, and applications'},
    {'name': 'Natural Language Processing', 'subject_code': 'CS507', 'year': '4th Year', 'semester': '2nd Semester',
     'description': 'Text processing, NLP models, and applications'},
    {'name': 'Project Work', 'subject_code': 'CS508', 'year': '4th Year', 'semester': '2nd Semester',
     'description': 'Major project and dissertation'},
]

with app.app_context():
    added = 0
    for sub_data in ENGINEERING_SUBJECTS:
        existing = Subject.query.filter_by(
            name=sub_data['name'], year=sub_data['year'], semester=sub_data['semester']
        ).first()
        if not existing:
            db.session.add(Subject(**sub_data))
            added += 1

    demo_student = User.query.filter_by(email='student@demo.com').first()
    if not demo_student:
        student = User(name='Demo Student', email='student@demo.com', role='student')
        student.set_password('student123')
        db.session.add(student)

    db.session.commit()
    print(f'Engineering subjects seeded! ({added} new subjects added)')
    print('Demo student: student@demo.com / student123')
    print('Admin: admin@smartnotes.ai / admin123')
