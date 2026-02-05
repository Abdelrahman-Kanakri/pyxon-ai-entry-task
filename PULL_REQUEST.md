# AI-Powered Document Parser with RAG Integration

## Summary

A production-ready AI document parser that intelligently processes documents (PDF, DOCX, TXT, Images), understands their content through semantic analysis, and prepares them for RAG systems with full Arabic language support including diacritics (harakat/tashkeel).

---

## Contact Information

📧 **Email:** `[YOUR_EMAIL_HERE]` - **REQUIRED**  
📱 **Phone:** `[YOUR_PHONE_HERE]` (optional)

---

## Demo Link

🔗 **Live Demo:** `[YOUR_DEMO_LINK_HERE]` - **REQUIRED**

---

## Features Implemented

- [x] Document parsing (PDF, DOCX, TXT, Images via OCR)
- [x] Content analysis and intelligent chunking strategy selection
- [x] Fixed and dynamic chunking strategies
- [x] Vector DB integration (ChromaDB)
- [x] SQL DB integration (PostgreSQL/SQLite)
- [x] Arabic language support with diacritics
- [x] Hybrid retrieval (semantic + keyword-based)
- [x] Benchmark suite with Arabic test cases
- [x] RAG integration with LLM support (Mistral/Google GenAI)
- [x] Streamlit web interface

---

## Architecture

### System Overview

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐
│   User/Client   │────▶│              FastAPI Gateway                 │
└─────────────────┘     └──────────────────────────────────────────────┘
                                          │
          ┌───────────────────────────────┼───────────────────────────────┐
          ▼                               ▼                               ▼
┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
│  PDF Extractor  │           │ DOCX Extractor  │           │ Image/OCR/TXT   │
│  (pdfplumber)   │           │  (python-docx)  │           │  (pytesseract)  │
└─────────────────┘           └─────────────────┘           └─────────────────┘
          │                               │                               │
          └───────────────────────────────┼───────────────────────────────┘
                                          ▼
                              ┌─────────────────────┐
                              │ Document Classifier │
                              │  (Complexity Score) │
                              └─────────────────────┘
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                           ▼
          ┌─────────────────┐                         ┌─────────────────┐
          │  Fixed Chunker  │                         │ Dynamic Chunker │
          │ (Simple Docs)   │                         │ (Complex Docs)  │
          └─────────────────┘                         └─────────────────┘
                    │                                           │
                    └─────────────────────┬─────────────────────┘
                                          ▼
                              ┌─────────────────────┐
                              │   Chunk Validator   │
                              └─────────────────────┘
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                           ▼
          ┌─────────────────┐                         ┌─────────────────┐
          │   ChromaDB      │                         │   PostgreSQL    │
          │ (Vector Store)  │                         │  (SQL Store)    │
          └─────────────────┘                         └─────────────────┘
                    │                                           │
                    └─────────────────────┬─────────────────────┘
                                          ▼
                              ┌─────────────────────┐
                              │  Hybrid Retriever   │
                              │ + Cross-Encoder     │
                              │    Reranker         │
                              └─────────────────────┘
                                          │
                                          ▼
                              ┌─────────────────────┐
                              │   LLM Interpreter   │
                              │ (Mistral/Gemini)    │
                              └─────────────────────┘
```

### Key Components

| Component               | Purpose                       | Technology                           |
| ----------------------- | ----------------------------- | ------------------------------------ |
| **Ingestion Layer**     | Multi-format document parsing | pdfplumber, python-docx, pytesseract |
| **Document Classifier** | Analyzes structure complexity | spaCy, custom heuristics             |
| **Chunking Engine**     | Fixed/Dynamic strategies      | LangChain text splitters             |
| **Vector Store**        | Semantic embeddings storage   | ChromaDB + multilingual-e5-small     |
| **SQL Store**           | Metadata & structured data    | PostgreSQL/SQLite + SQLAlchemy       |
| **Retriever**           | Hybrid search                 | Semantic + keyword matching          |
| **RAG Pipeline**        | Answer synthesis              | Mistral AI / Google GenAI            |

---

## Architecture Decisions & Trade-offs

| Decision                    | Alternative Considered     | Reason for Choice                                  | Trade-off                          |
| --------------------------- | -------------------------- | -------------------------------------------------- | ---------------------------------- |
| **ChromaDB (Persistent)**   | Pinecone, Weaviate         | Zero-config, embedded, free for MVP                | Limited horizontal scaling         |
| **multilingual-e5-small**   | OpenAI Embeddings, AraBERT | Excellent Arabic+English, local inference, privacy | Higher CPU usage vs API embeddings |
| **Dual-Store (Vector+SQL)** | Single Vector DB           | ACID compliance for metadata, rich SQL queries     | Sync complexity handled by Indexer |
| **pytesseract (Sync)**      | Async Celery workers       | Simpler deployment, no Redis/workers needed        | Blocks thread on large images      |
| **Dynamic Chunking**        | Fixed-size only            | Preserves semantic boundaries in complex docs      | Slightly higher processing time    |
| **Hybrid Retrieval**        | Semantic-only              | Better recall for keyword-heavy queries            | More complex pipeline              |

---

## Technologies Used

### Core Stack

- **API Framework:** FastAPI
- **UI:** Streamlit
- **Database:** PostgreSQL/SQLite (via SQLAlchemy)
- **Vector Store:** ChromaDB

### Document Processing

- **PDF:** pdfplumber, pypdf
- **DOCX:** python-docx
- **Images/OCR:** pytesseract, Pillow
- **TXT:** Custom encoding detection

### NLP & Embeddings

- **Embeddings:** sentence-transformers (`intfloat/multilingual-e5-small`)
- **NLP:** spaCy (multilingual)
- **Arabic Support:** camel-tools, custom diacritics handling
- **Reranking:** Cross-encoder models

### LLM Integration

- **Providers:** Mistral AI, Google GenAI (Gemini)
- **Orchestration:** LangChain

---

## Benchmark Results

### Retrieval Accuracy

| Metric                         | Score    | Notes                                      |
| ------------------------------ | -------- | ------------------------------------------ |
| **Hit Rate (@k=3)**            | **100%** | Perfect recall on technical domain dataset |
| **MRR (Mean Reciprocal Rank)** | **1.0**  | Correct answer consistently ranked #1      |

### Performance Latency

| Operation             | Avg Time | Hardware Context                    |
| --------------------- | -------- | ----------------------------------- |
| **Indexing (1 Page)** | ~1200ms  | Includes embedding generation (CPU) |
| **Retrieval Query**   | ~350ms   | Vector search + reranking           |
| **End-to-End RAG**    | ~4500ms  | Includes LLM generation latency     |

### Test Queries (including Arabic)

```python
TEST_QUERIES = [
    {"query": "Who is the CEO of Pyxon AI?", "expected_terms": ["Sarah Connor", "Cyberdyne"]},
    {"query": "What formats does PyxonParser support?", "expected_terms": ["PDF", "DOCX", "Images"]},
    {"query": "Where is the headquarters located?", "expected_terms": ["Amman", "Jordan"]},
    {"query": "What is Semantic Density?", "expected_terms": ["complete information units", "metric"]},
    {"query": "أين يقع المقر الرئيسي لشركة بيكسون؟", "expected_terms": ["عمان", "الأردن"]},  # Arabic
]
```

---

## How to Run

### Prerequisites

- Python 3.11+
- PostgreSQL 12+ (optional, SQLite works out of box)
- Tesseract OCR (for image processing)

### Quick Start

```bash
# Clone repository
git clone https://github.com/Abdelrahman-Kanakri/pyxon-ai-entry-task.git
cd pyxon-ai-entry-task

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (MISTRAL_API_KEY, GOOGLE_GENAI_API_KEY)

# Run API server
uvicorn api.main:app --reload --port 8000

# Run Streamlit UI (separate terminal)
streamlit run interface/app.py
```

### Docker Deployment

```bash
docker build -t pyxon-parser .
docker run -p 7860:7860 --env-file .env pyxon-parser
```

---

## Questions & Assumptions

### Questions

1. **Embedding Model Choice:** Should we prioritize dedicated Arabic models (AraBERT) over multilingual models (E5)?
   - **Assumption:** Used `multilingual-e5-small` for balanced Arabic+English performance with lower resource usage.

2. **Graph RAG Implementation:** The requirements mention Graph RAG as "consider implementing." Is this mandatory?
   - **Assumption:** Focused on Hybrid Retrieval which is fully implemented; Graph RAG listed as future enhancement.

3. **OCR Language Priority:** Should Arabic OCR take precedence over English when both are detected?
   - **Assumption:** Used `ara+eng` combined mode in Tesseract for best mixed-language results.

4. **Chunk Size for Arabic:** Arabic text is denser than English. Should chunk sizes be adjusted?
   - **Assumption:** Used standard 512-token chunks with 50-token overlap; dynamic chunking handles semantic boundaries.

---

## Project Structure

```
pyxon-ai-entry-task/
├── api/                    # FastAPI routes
├── interface/              # Streamlit UI
│   └── app.py
├── src/
│   ├── chunking/          # Fixed & dynamic chunking
│   ├── config/            # Settings & constants
│   ├── ingestion/         # Document extractors (PDF, DOCX, TXT, Image)
│   ├── knowledge_store/   # Vector DB & SQL DB
│   ├── parsing/           # Classifiers & semantic extraction
│   └── rag_layer/         # Retriever, reranker, context formatting
├── benchmarks/            # Benchmark suite
├── docs/                  # Documentation
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Future Improvements

1. **Graph RAG:** Implement knowledge graphs for document relationship modeling
2. **RAPTOR:** Add hierarchical chunking with abstractive summarization
3. **Async OCR:** Move image processing to background workers (Celery + Redis)
4. **Fine-tuned Arabic Model:** Train or fine-tune AraBERT for domain-specific Arabic content
5. **Streaming Responses:** Implement SSE for real-time LLM output streaming
6. **Multi-tenant Support:** Add user authentication and document isolation

---

**Author:** Abdelrahman Belal Kanakri  
**Submission Date:** February 2, 2026
