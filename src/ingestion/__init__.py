"""
Ingestion Module

Handles document loading and extraction from multiple file formats
(PDF, DOCX, TXT) with robust error handling and metadata extraction.

Components:
- base.py: Abstract base classes for extractors
- pdf_extractor.py: PDF document extraction
- docx_extractor.py: DOCX document extraction
- txt_extractor.py: Text file extraction
- loader.py: Factory pattern for document loading

Example:
    from src.ingestion import DocumentLoader
    
    content = DocumentLoader.load_document("path/to/document.pdf")
    print(f"Extracted {content.page_count} pages")
    print(f"Language: {content.language}")
    print(f"Confidence: {content.extraction_confidence}")
"""

from .base import (
    BaseExtractor,
    TextExtractor,
    ImageExtractor,
    ExtractedContent,
    ExtractionMetadata,
    ExtractionStatus,
)
from .pdf_extractor import PDFExtractor
from .docx_extractor import DOCXExtractor
from .txt_extractor import TXTExtractor
from .loader import DocumentLoader

__all__ = [
    "DocumentLoader",
    "BaseExtractor",
    "TextExtractor",
    "ImageExtractor",
    "PDFExtractor",
    "DOCXExtractor",
    "TXTExtractor",
    "ExtractedContent",
    "ExtractionMetadata",
    "ExtractionStatus",
]
