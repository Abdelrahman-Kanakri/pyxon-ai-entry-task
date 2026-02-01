"""
PDF Document Extractor

Handles extraction of text and structure from PDF files.
Uses pdfplumber for advanced PDF processing and PyPDF2 for fallback.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import time
import logging
from typing import Dict, List, Any, Optional

# Optional imports with graceful fallback
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    logger = logging.getLogger(__name__)
    logger.warning("pdfplumber not available, PDF extraction will be limited")

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

from .base import BaseExtractor, ExtractedContent, ExtractionMetadata, ExtractionStatus

logger = logging.getLogger(__name__)


class PDFExtractor(BaseExtractor):
    """Extract content from PDF files using pdfplumber."""
    
    def _is_supported_format(self) -> bool:
        """Check if file is a PDF."""
        return self.file_path.suffix.lower() == ".pdf"
    
    def extract(self) -> ExtractedContent:
        """
        Extract content from PDF file.
        
        Returns:
            ExtractedContent: Extracted text and structure
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            raw_text = ""
            structured_data = {}
            extracted_tables = []
            
            with pdfplumber.open(self.file_path) as pdf:
                page_count = len(pdf.pages)
                
                # Extract text and structure from each page
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # Extract text
                        page_text = page.extract_text() or ""
                        raw_text += f"\n--- Page {page_num} ---\n{page_text}"
                        
                        # Extract tables
                        tables = page.extract_tables()
                        if tables:
                            for table_idx, table in enumerate(tables):
                                extracted_tables.append({
                                    "page": page_num,
                                    "table_index": table_idx,
                                    "data": table,
                                    "extracted_text": self._table_to_text(table)
                                })
                        
                        # Extract layout information
                        if "layout" not in structured_data:
                            structured_data["layout"] = {}
                        
                        structured_data["layout"][f"page_{page_num}"] = {
                            "width": page.width,
                            "height": page.height,
                            "text_length": len(page_text),
                            "table_count": len(tables) if tables else 0
                        }
                        
                    except Exception as page_error:
                        warnings.append(f"Error extracting page {page_num}: {str(page_error)}")
                        logger.warning(f"Page extraction error: {page_error}")
                
                # Try to extract metadata
                try:
                    if pdf.metadata:
                        structured_data["metadata"] = dict(pdf.metadata)
                except Exception as meta_error:
                    warnings.append(f"Could not extract metadata: {str(meta_error)}")
            
            # Fallback to pypdf if pdfplumber failed to extract meaningful text
            if len(raw_text.strip()) < 50:
                self.logger.warning("pdfplumber extracted insufficient text, trying pypdf fallback")
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(self.file_path)
                    fallback_text = []
                    
                    for i, page in enumerate(reader.pages):
                        text = page.extract_text() or ""
                        fallback_text.append(f"\n--- Page {i+1} ---\n{text}")
                    
                    if len("".join(fallback_text).strip()) > len(raw_text.strip()):
                        raw_text = "".join(fallback_text)
                        self.logger.info(f"pypdf fallback used, extracted {len(raw_text)} chars")
                except Exception as e:
                    self.logger.error(f"pypdf fallback failed: {e}")
                    warnings.append(f"Fallback extraction failed: {str(e)}")

            # Tertiary fallback to pdfminer.six (most robust but slower)
            if len(raw_text.strip()) < 50:
                self.logger.warning("pypdf extraction insufficient, trying pdfminer.six fallback")
                try:
                    from pdfminer.high_level import extract_text
                    text = extract_text(self.file_path)
                    if text and len(text.strip()) > len(raw_text.strip()):
                        raw_text = text
                        self.logger.info(f"pdfminer.six fallback used, extracted {len(raw_text)} chars")
                except Exception as e:
                    self.logger.error(f"pdfminer.six fallback failed: {e}")
                    warnings.append(f"All extraction methods failed or returned minimal text: {str(e)}")

            # Clean the text
            cleaned_text = self._clean_text(raw_text)
            
            # Detect language
            language = self._detect_language(cleaned_text)
            
            # Calculate confidence
            confidence = min(len(cleaned_text) / 1000, 1.0)  # Rough estimate
            
            extraction_time = time.time() - start_time
            
            return ExtractedContent(
                raw_text=raw_text,
                cleaned_text=cleaned_text,
                structured_data=structured_data,
                language=language,
                page_count=page_count,
                extracted_tables=extracted_tables,
                images_extracted=0,
                extraction_confidence=confidence,
                metadata={
                    "extraction_time": extraction_time,
                    "file_size": self.get_file_size(),
                    "encoding": "utf-8"
                },
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            errors.append(f"Extraction failed: {str(e)}")
            
            # Return partial content on error
            return ExtractedContent(
                raw_text="",
                cleaned_text="",
                structured_data={},
                language="unknown",
                page_count=0,
                extracted_tables=[],
                images_extracted=0,
                extraction_confidence=0.0,
                metadata={},
                errors=errors,
                warnings=warnings
            )
    
    def get_metadata(self) -> ExtractionMetadata:
        """Get extraction metadata."""
        start_time = time.time()
        
        try:
            with pdfplumber.open(self.file_path) as pdf:
                page_count = len(pdf.pages)
        except Exception:
            page_count = 0
        
        extraction_time = time.time() - start_time
        
        return ExtractionMetadata(
            source_file=str(self.file_path),
            extraction_time=extraction_time,
            file_size_bytes=self.get_file_size(),
            encoder_used="utf-8",
            status=ExtractionStatus.SUCCESS
        )
    
    def get_page_count(self) -> int:
        """Get total number of pages in PDF."""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                return len(pdf.pages)
        except Exception as e:
            logger.error(f"Error reading page count: {e}")
            return 0
    
    def extract_page_text(self, page_number: int) -> str:
        """
        Extract text from specific page.
        
        Args:
            page_number: Page number (1-indexed)
            
        Returns:
            Text from the page
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                if page_number < 1 or page_number > len(pdf.pages):
                    raise IndexError(f"Page {page_number} out of range")
                
                page = pdf.pages[page_number - 1]
                return page.extract_text() or ""
        except Exception as e:
            logger.error(f"Error extracting page {page_number}: {e}")
            return ""
    
    @staticmethod
    def _table_to_text(table: List[List[Any]]) -> str:
        """Convert table to text format."""
        text_rows = []
        for row in table:
            row_text = " | ".join(str(cell) if cell else "" for cell in row)
            text_rows.append(row_text)
        return "\n".join(text_rows)
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        lines = text.split("\n")
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(cleaned_lines)
    
    @staticmethod
    def _detect_language(text: str) -> str:
        """
        Simple language detection.
        
        Args:
            text: Text to detect language for
            
        Returns:
            Language code: 'en', 'ar', or 'mixed'
        """
        if not text:
            return "unknown"
        
        # Count Arabic and English characters
        arabic_chars = sum(1 for c in text if ord(c) >= 0x0600 and ord(c) <= 0x06FF)
        english_chars = sum(1 for c in text if ord(c) >= 0x0041 and ord(c) <= 0x007A)
        
        total_chars = arabic_chars + english_chars
        
        if total_chars == 0:
            return "unknown"
        
        arabic_ratio = arabic_chars / total_chars
        
        if arabic_ratio > 0.7:
            return "ar"
        elif arabic_ratio < 0.3:
            return "en"
        else:
            return "mixed"
