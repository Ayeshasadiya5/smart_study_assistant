from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)

    chat_history = db.relationship('ChatHistory', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subject_code = db.Column(db.String(50), nullable=True)
    year = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)

    materials = db.relationship('StudyMaterial', backref='subject', lazy=True)
    chat_history = db.relationship('ChatHistory', backref='subject', lazy=True)

    def __repr__(self):
        return f'<Subject {self.name}>'


class StudyMaterial(db.Model):
    __tablename__ = 'study_materials'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    year = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    material_type = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StudyMaterial {self.title}>'


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    subject_name = db.Column(db.String(200), nullable=True)
    year = db.Column(db.String(50), nullable=True)
    semester = db.Column(db.String(50), nullable=True)
    regulation = db.Column(db.String(20), nullable=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class SearchHistory(db.Model):
    __tablename__ = 'search_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    year = db.Column(db.String(50), nullable=True)
    semester = db.Column(db.String(50), nullable=True)
    regulation = db.Column(db.String(20), nullable=True)
    subject_name = db.Column(db.String(200), nullable=False)
    search_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='search_history', lazy=True)
