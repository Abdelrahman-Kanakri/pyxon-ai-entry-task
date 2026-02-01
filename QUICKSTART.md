# Quick Start Guide

## Current Status

✅ API implementation complete  
✅ Interface implementation complete  
⚠️ Dependency installation in progress

## Getting the System Running

### Step 1: Install Core Dependencies

The full `requirements.txt` has many optional packages. For a quick start, install just the essentials:

```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Install core packages
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv python-multipart sqlalchemy streamlit requests

# Optional: For full functionality
pip install sentence-transformers chromadb python-docx pypdf psycopg2-binary
```

### Step 2: Set Up Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Minimum required
DATABASE_URL=postgresql://user:password@localhost/dbname
# Or use SQLite for testing:
# DATABASE_URL=sqlite:///./data/app.db

CHROMA_DB_PATH=./data/chroma

# Optional: For LLM features
MISTRAL_API_KEY=your_key_here
GOOGLE_GENAI_API_KEY=your_key_here
```

### Step 3: Start the API Server

```bash
cd c:\Users\abdel\OneDrive\Desktop\pyxon-ai-entry-task
.\.venv\Scripts\activate
uvicorn api.main:app --reload --port 8000
```

Visit: http://localhost:8000/docs for API documentation

### Step 4: Start the Streamlit Interface

In a **new terminal**:

```bash
cd c:\Users\Desktop\pyxon-ai-entry-task
.\.venv\Scripts\activate
streamlit run interface\app.py
```

Visit: http://localhost:8501

## Testing

### Quick API Test (PowerShell)

```powershell
# Health check
curl http://localhost:8000/api/v1/health

# Or use browser
# Navigate to: http://localhost:8000/docs
```

### Upload a Document

1. Go to http://localhost:8501
2. Click "📤 Upload Documents"
3. Select a PDF, DOCX, or TXT file
4. Click "Process Document"

### Query Documents

1. Go to "🔍 Query Documents"
2. Enter a question
3. View results with scores

## Troubleshooting

### ModuleNotFoundError

- Make sure virtual environment is activated
- Run: `pip install pydantic-settings`

### Database Connection Error

- Check DATABASE_URL in `.env`
- For testing, use SQLite: `sqlite:///./data/app.db`

### Port Already in Use

- Kill existing process or use different port:
  ```bash
  uvicorn api.main:app --reload --port 8001
  ```

## System Requirements

- **Python**: 3.8+ (currently using 3.8.10)
- **Database**: PostgreSQL or SQLite
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for models and data

## Notes

- Some ML features require additional packages (torch, transformers, spacy)
- The system will gracefully degrade if optional packages are missing
- Core document processing works without ML dependencies
