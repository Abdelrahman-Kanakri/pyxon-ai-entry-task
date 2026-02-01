# Quick Start Guide

**Get up and running with Pyxon AI Document Parser in 5 minutes**

---

## ⚡ TL;DR (Quick Start)

```bash
# 1. Setup
git clone <repo-url> && cd pyxon-ai-entry-task
python -m venv venv && source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your database credentials

# 3. Initialize
createdb pyxon_parser
python -m alembic upgrade head

# 4. Test
python -c "from src.ingestion import DocumentLoader; print(DocumentLoader.get_supported_formats())"

# 5. Use
python
```

```python
from src.ingestion import DocumentLoader

# Load document
content = DocumentLoader.load_document("document.pdf")

# Access results
print(f"Pages: {content.page_count}")
print(f"Language: {content.language}")
print(f"Text preview: {content.cleaned_text[:200]}")
```

---

## 🎯 Common Tasks

### Load a PDF Document

```python
from src.ingestion import DocumentLoader

content = DocumentLoader.load_document("myfile.pdf")
print(content.cleaned_text)
```

### Process a DOCX Document

```python
content = DocumentLoader.load_document("myfile.docx")

# Access structure
print(f"Headings: {content.structured_data['headings']}")
print(f"Tables: {len(content.extracted_tables)}")
```

### Batch Process Multiple Files

```python
from pathlib import Path
from src.ingestion import DocumentLoader

for file in Path(".").glob("*.pdf"):
    content = DocumentLoader.load_document(file)
    print(f"{file.name}: {content.page_count} pages")
```

### Check File Before Processing

```python
if DocumentLoader.validate_file("myfile.pdf"):
    content = DocumentLoader.load_document("myfile.pdf")
else:
    print("File not supported")
```

### Get File Information

```python
info = DocumentLoader.get_file_info("myfile.pdf")
print(f"Size: {info['size_mb']} MB")
print(f"Type: {info['extension']}")
```

---

## 🔧 Configuration Essentials

### Minimum .env Setup

```ini
# Database (required)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pyxon_parser
DB_USER=postgres
DB_PASSWORD=your_password

# Optional but recommended
OPENAI_API_KEY=sk-your-key
CHUNK_SIZE=512
CHROMA_DB_PATH=./data/chroma_db
```

### Get Database Password

```bash
# PostgreSQL default user
sudo -u postgres psql

# Set password
postgres=# ALTER USER postgres WITH PASSWORD 'your_password';
postgres=# \q
```

---

## 📊 Supported Formats

| Format | Status | Features |
|--------|--------|----------|
| PDF | ✅ Ready | Text, tables, metadata |
| DOCX | ✅ Ready | Structure, styles, tables |
| DOC | ✅ Ready | Basic text extraction |
| TXT | ✅ Ready | Encoding detection |

---

## 🐛 Quick Troubleshooting

### "ModuleNotFoundError"

```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt
```

### "Database connection error"

```bash
# Check PostgreSQL is running
psql --version

# Start PostgreSQL
brew services start postgresql  # macOS
sudo service postgresql start   # Linux
# Windows: Use PostgreSQL GUI or pgAdmin
```

### "File not found"

```python
# Check file exists and path is correct
from pathlib import Path
file = Path("document.pdf")
print(file.exists())  # Should be True
```

### Encoding errors with TXT files

```python
# The system auto-detects encoding, but if it fails:
# Convert to UTF-8 first
# Linux/macOS:
iconv -f ISO-8859-1 -t UTF-8 file.txt > file_utf8.txt
```

---

## 📚 Next Steps

1. **Read Full User Guide:** [USER_GUIDE.md](./USER_GUIDE.md)
2. **Review Implementation:** [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
3. **Explore Ingestion Layer:** [02_INGESTION_IMPLEMENTATION.md](./02_INGESTION_IMPLEMENTATION.md)
4. **Check Configuration:** [01_CONFIGURATION_IMPLEMENTATION.md](./01_CONFIGURATION_IMPLEMENTATION.md)

---

## 🤝 Need Help?

- **Documentation:** Check `/docs` folder
- **Examples:** Search for `Example:` in code
- **Errors:** Check error message and logs in `./logs/app.log`
- **GitHub Issues:** Submit with error details

---

## 💡 Pro Tips

1. **Use absolute paths** for file operations
2. **Check confidence score** - if < 0.3, extraction may be poor
3. **Check warnings** - content.warnings may indicate issues
4. **Validate first** - use DocumentLoader.validate_file() before loading
5. **Enable logging** - set LOG_LEVEL=DEBUG in .env for detailed logs

---

**Ready to process your first document?** Start with the code examples above! 🚀
