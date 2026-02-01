# Pyxon AI Document Parser - User Guide

**Version:** 1.0.0  
**Date:** February 1, 2026

## 👋 Introduction

Welcome to the **Pyxon AI Document Parser** dashboard. This application allows you to upload documents (PDF, DOCX, TXT), automatically extract their content (including Arabic text), and perform intelligent questions-and-answers on your document knowledge base.

---

## 🚀 Getting Started

### Accessing the Dashboard

1. Open your web browser.
2. Navigate to: `http://localhost:8501`
3. You will see the main interface with the sidebar navigation.

---

## 📂 1. Uploading Documents

Go to the **"📂 Upload Document"** page from the sidebar.

### Steps:

1. **Choose a file**: Click "Browse files" or drag-and-drop your document.
   - _Supported formats_: PDF, DOCX, TXT.
   - _Max size_: 50MB.
2. **Review Details**: The system will preview the filename and size.
3. **Click "Upload Document"**:
   - The system will extract text, detect language, and index the content.
   - **Green Success Message**: Look for `(Lang: XX)` to see the detected language (e.g., `ar` for Arabic, `en` for English).

> **Note**: For scanning/image-based PDFs, the system will attempt to extract text using OCR if enabled by the administrator.

---

## 🔍 2. Querying Documents

Go to the **"🔍 Query Documents"** page.

This is where you can ask questions about your uploaded documents.

### How to Search:

1. **Enter Question**: Type a natural language question (e.g., _"What is the main conclusion of the study?"_ or _"Summarize the financial results"_).
2. **Select Results (Top K)**: Choose how many text chunks to retrieve (default is 5).
3. **Click "Search"**.

### Understanding Results:

- The system searches _all_ uploaded documents.
- **Results List**: Shows the most relevant text segments found.
- **Source Info**: Each result shows:
  - **📄 Filename**: The exact document the answer came from.
  - **Score**: Relevance score (higher is better).
  - **Content**: The actual text snippet.

---

## 📊 3. Managing Documents

Go to the **"📊 Document List"** page.

Here you can see everything stored in the system.

- **Refresh List**: Click to reload the database view.
- **View Details**:
  - **ID**: Unique system ID.
  - **Type**: File format (PDF/DOCX).
  - **Pages**: Page count.
  - **Language**: Detected language (e.g., `ar`, `en`).
  - **Uploaded**: Date and time.
- **Delete**: Click the "🗑️ Delete" button to permanently remove a document and its index.

---

## ❓ FAQ

**Q: My Arabic PDF shows "Lang: Unknown", what does that mean?**
A: This usually means the PDF is a scanned image (no selectable text). The system uses AI to detect language, so if it can't read text, it can't detect language. Ensure your PDF has selectable text.

**Q: Can I search in Arabic?**
A: Yes! The system supports multilingual semantic search. You can search Arabic documents using English queries and vice-versa.

**Q: Where can I find help?**
A: Contact the system administrator or refer to the `TECHNICAL_MANUAL.md` for backend issues.
