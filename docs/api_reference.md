# Pyxon AI Documentation - API Reference

## FastAPI Endpoints

### Base URL

```
http://localhost:8000/api/v1
```

### Health Check Endpoints

#### GET /health

Basic health check.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-02-01T12:00:00"
}
```

#### GET /health/db

Database connection health check.

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-01T12:00:00"
}
```

---

### Document Processing Endpoints

#### POST /parse/upload

Upload and process a document.

**Request:** Multipart form data with file

**Response:**

```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "status": "completed",
  "chunk_count": 25,
  "message": "Document processed successfully"
}
```

#### GET /parse/documents

List all processed documents.

**Response:**

```json
{
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document.pdf",
      "file_type": "pdf",
      "page_count": 10,
      "upload_date": "2026-02-01T12:00:00",
      "language": "en"
    }
  ],
  "total": 1
}
```

#### DELETE /parse/document/{document_id}

Delete a document.

**Response:**

```json
{
  "message": "Document deleted successfully",
  "document_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Retrieval Endpoints

#### POST /retrieval/query

Query documents using RAG retrieval.

**Request:**

```json
{
  "query": "What is the main topic?",
  "top_k": 5,
  "document_id": null
}
```

**Response:**

```json
{
  "query": "What is the main topic?",
  "chunks": [
    {
      "content": "The document discusses...",
      "score": 0.95,
      "metadata": {
        "document_id": "550e8400-e29b-41d4-a716-446655440000",
        "chunk_index": 0
      }
    }
  ],
  "total_results": 5
}
```

---

## Streamlit Interface

### Access

```
http://localhost:8501
```

### Pages

1. **Upload Documents** - Upload PDF, DOCX, TXT files
2. **Query Documents** - Search across all documents
3. **Document List** - View and manage processed documents

---

## Running the Services

### Start API Server

```bash
cd c:\Users\abdel\OneDrive\Desktop\pyxon-ai-entry-task
.\.venv\Scripts\activate
uvicorn api.main:app --reload --port 8000
```

### Start Streamlit Interface

```bash
cd c:\Users\abdel\OneDrive\Desktop\pyxon-ai-entry-task
.\.venv\Scripts\activate
streamlit run interface\app.py
```
