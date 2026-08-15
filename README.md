# Smart Student Notes & AI Doubt Assistant

A complete web application that helps college students find study materials by year, semester, and subject, with an AI-powered chatbot for academic doubts using Retrieval-Augmented Generation (RAG).

## Features

- **Study Material Search** — Filter PDFs by year, semester, subject, unit, material type, and keyword
- **PDF Viewer** — View and download PDFs directly in the browser
- **AI Doubt Assistant** — Ask academic questions with context from uploaded study materials
- **RAG Pipeline** — PDF text extraction, chunking, embedding, and FAISS vector search
- **Important Questions Generator** — AI-generated exam preparation questions
- **Admin Dashboard** — Manage subjects, upload/delete PDFs with automatic RAG processing
- **Authentication** — Student registration/login and admin login with secure password hashing
- **Session Context** — AI knows the student's current year, semester, and subject selection

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5, Font Awesome |
| Backend | Python, Flask |
| Database | SQLite, SQLAlchemy |
| PDF Processing | PyMuPDF (fitz) |
| AI | Google Gemini API |
| RAG | LangChain, FAISS, Gemini Embeddings |

## Architecture

```
Student Browser
      │
      ▼
Flask Application (app.py)
      │
      ├── routes/ (auth, student, admin, ai)
      ├── services/ (pdf_processor, rag_service, ai_service, search_service)
      ├── database/ (SQLAlchemy models)
      │
      ├── SQLite Database (users, subjects, materials, chat_history)
      ├── uploads/ (PDF files)
      └── vectorstore/ (FAISS embeddings per material)
```

### RAG Flow

1. Admin uploads a PDF
2. PyMuPDF extracts text with page numbers
3. Text is cleaned and split into chunks
4. Gemini embeddings are generated
5. Chunks stored in FAISS vector store
6. Student asks a question
7. Relevant chunks retrieved via similarity search
8. Context + question sent to Gemini
9. Answer returned with source citations

## Folder Structure

```
SmartNotesAI/
├── app.py                  # Flask application entry point
├── config.py               # Configuration and environment variables
├── requirements.txt        # Python dependencies
├── seed_data.py            # Sample data seeder
├── .env.example            # Environment variable template
├── database/
│   ├── models.py           # SQLAlchemy models
├── routes/
│   ├── auth.py             # Login, register, logout
│   ├── student.py          # Dashboard, materials, PDF viewer
│   ├── admin.py            # Admin dashboard, upload, delete
│   └── ai.py               # Chatbot and question generation APIs
├── services/
│   ├── pdf_processor.py    # PDF validation and text extraction
│   ├── rag_service.py      # FAISS vector store and search
│   ├── ai_service.py       # Gemini AI integration
│   └── search_service.py   # Material search and filtering
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS and JavaScript
├── uploads/                # Uploaded PDF files
└── vectorstore/            # FAISS index files
```

## Installation

### 1. Clone or navigate to the project

```bash
cd SmartNotesAI
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and add your keys:

```bash
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux
```

Edit `.env`:

```text
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_random_secret_key_here
```

Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

### 5. Seed sample data (optional)

```bash
python seed_data.py
```

### 6. Run the application

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Default Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@smartnotes.ai | admin123 |
| Demo Student | student@demo.com | student123 |

**Change the admin password after first login in production.**

## How to Upload PDFs

1. Login as admin (`admin@smartnotes.ai` / `admin123`)
2. Go to **Admin Dashboard**
3. Add subjects (year, semester, name)
4. Click **Upload PDF**
5. Fill in title, year, semester, subject, material type, unit, and description
6. Select a PDF file (max 16 MB)
7. Click **Upload PDF**

The PDF is automatically processed for AI search after upload.

## How to Use the AI Chatbot

1. Login as a student
2. Select year, semester, and subject on the dashboard
3. Click **AI Doubt Assistant** or **Ask your doubt**
4. Type your academic question and press Enter
5. The AI searches relevant study materials and provides an answer with source citations

When viewing a specific PDF, click **Ask AI about this PDF** to get answers scoped to that document.

## How to Generate Important Questions

1. Go to **Questions** from the navigation or dashboard
2. Select a subject and optionally a unit
3. Click **Generate**
4. AI-generated questions appear labeled as **AI-Generated**

## Database Tables

- **users** — Students and admins with hashed passwords
- **subjects** — Subject catalog with year and semester
- **study_materials** — PDF metadata and file paths
- **chat_history** — Stored AI conversations

## Error Handling

The application shows friendly messages for:

- Invalid login credentials
- Duplicate registration
- Missing subjects or PDFs
- Invalid or oversized PDF uploads
- AI API failures
- Missing API key (AI features gracefully disabled)

## Future Improvements

- Email verification for student accounts
- Bulk PDF upload
- Bookmarking favorite materials
- Chat history viewer for students
- Role-based subject assignment
- Cloud storage for PDFs (S3/GCS)
- Multi-language support
- Mobile app (React Native / Flutter)
- Analytics dashboard for admin
- OCR support for scanned PDFs

## License

This project is intended for educational and mini-project use.
