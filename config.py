import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'dev-secret-key-change-in-production'
    )

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'smartnotes.db')
    )

    # Support Neon/PostgreSQL URLs
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://",
            "postgresql://",
            1
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Folders
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    VECTORSTORE_FOLDER = os.path.join(BASE_DIR, 'vectorstore')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '')

    # AI Models
    EMBEDDING_MODEL = 'models/embedding-001'
    GEMINI_MODEL = 'gemini-3.6-flash'

    # Study Material Types
    MATERIAL_TYPES = [
        'Lecture Notes',
        'Unit Notes',
        'Important Questions',
        'Previous Mid Paper',
        'Previous Semester Paper',
        'Assignment',
        'Study Material',
        'Other',
    ]

    # Academic Years
    YEARS = [
        '1st Year',
        '2nd Year',
        '3rd Year',
        '4th Year'
    ]

    # Semesters
    SEMESTERS = [
        '1st Semester',
        '2nd Semester'
    ]

    # Regulations
    REGULATIONS = [
        'R23',
        'R20',
        'R19',
        'R18'
    ]

    # Web Search Cache
    SEARCH_CACHE_TTL = int(
        os.environ.get(
            'SEARCH_CACHE_TTL',
            '3600'
        )
    )