import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'smartnotes.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    VECTORSTORE_FOLDER = os.path.join(BASE_DIR, 'vectorstore')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '')

    EMBEDDING_MODEL = 'models/embedding-001'
    GEMINI_MODEL = 'gemini-3.6-flash'

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

    YEARS = ['1st Year', '2nd Year', '3rd Year', '4th Year']
    SEMESTERS = ['1st Semester', '2nd Semester']
    REGULATIONS = ['R23', 'R20', 'R19', 'R18']

    # Web search (Google Custom Search API)
    SEARCH_CACHE_TTL = int(
    os.environ.get(
        'SEARCH_CACHE_TTL',
        '3600'
    )
)
     # 1 hour
