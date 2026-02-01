"""
DOCX Document Extractor

Handles extraction of text and structure from DOCX files.
Uses python-docx library for accurate processing.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import time
import logging
from typing import Dict, List, Any
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from .base import BaseExtractor, ExtractedContent, ExtractionMetadata, ExtractionStatus

logger = logging.getLogger(__name__)


class DOCXExtractor(BaseExtractor):
    """Extract content from DOCX files."""
    
    def _is_supported_format(self) -> bool:
        """Check if file is a DOCX or DOC."""
        return self.file_path.suffix.lower() in [".docx", ".doc"]
    
    def extract(self) -> ExtractedContent:
        """
        Extract content from DOCX file.
        
        Returns:
            ExtractedContent: Extracted text and structure
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            doc = Document(self.file_path)
            
            raw_text = ""
            structured_data = {
                "headings": [],
                "paragraphs": [],
                "sections": []
            }
            extracted_tables = []
            
            current_section = {"title": "Introduction", "content": []}
            
            # Extract text and structure
            for element in doc.element.body:
                try:
                    # Handle paragraphs
                    if element.tag.endswith("p"):
                        paragraph = Paragraph(element, doc)
                        text = paragraph.text
                        
                        if text.strip():
                            raw_text += text + "\n"
                            
                            # Detect heading styles
                            style = paragraph.style.name if paragraph.style else "Normal"
                            
                            if "Heading" in style:
                                current_section = {
                                    "title": text,
                                    "content": []
                                }
                                structured_data["headings"].append(text)
                                structured_data["sections"].append(current_section)
                            else:
                                structured_data["paragraphs"].append({
                                    "text": text,
                                    "style": style
                                })
                                if current_section:
                                    current_section["content"].append(text)
                    
                    # Handle tables
                    elif element.tag.endswith("tbl"):
                        table = Table(element, doc)
                        table_data = self._extract_table(table)
                        extracted_tables.append(table_data)
                        
                        # Add table text to raw text
                        raw_text += self._table_to_text(table_data["data"]) + "\n"
                
                except Exception as elem_error:
                    warnings.append(f"Error processing element: {str(elem_error)}")
                    logger.warning(f"Element processing error: {elem_error}")
            
            # Extract document properties
            try:
                if hasattr(doc, 'core_properties'):
                    props = doc.core_properties
                    structured_data["document_properties"] = {
                        "title": props.title,
                        "author": props.author,
                        "subject": props.subject,
                        "created": str(props.created) if props.created else None,
                        "modified": str(props.modified) if props.modified else None
                    }
            except Exception as props_error:
                warnings.append(f"Error extracting properties: {str(props_error)}")
            
            # Clean text
            cleaned_text = self._clean_text(raw_text)
            
            # Detect language
            language = self._detect_language(cleaned_text)
            
            # Calculate confidence
            confidence = min(len(cleaned_text) / 1000, 1.0)
            
            extraction_time = time.time() - start_time
            
            return ExtractedContent(
                raw_text=raw_text,
                cleaned_text=cleaned_text,
                structured_data=structured_data,
                language=language,
                page_count=self._estimate_page_count(len(raw_text)),
                extracted_tables=extracted_tables,
                images_extracted=0,
                extraction_confidence=confidence,
                metadata={
                    "extraction_time": extraction_time,
                    "file_size": self.get_file_size(),
                    "encoding": "utf-8",
                    "section_count": len(structured_data.get("sections", []))
                },
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"DOCX extraction failed: {str(e)}")
            errors.append(f"Extraction failed: {str(e)}")
            
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
            doc = Document(self.file_path)
            section_count = len(doc.sections)
        except Exception:
            section_count = 0
        
        extraction_time = time.time() - start_time
        
        return ExtractionMetadata(
            source_file=str(self.file_path),
            extraction_time=extraction_time,
            file_size_bytes=self.get_file_size(),
            encoder_used="utf-8",
            status=ExtractionStatus.SUCCESS
        )
    
    @staticmethod
    def _extract_table(table: Table) -> Dict[str, Any]:
        """
        Extract table data.
        
        Args:
            table: Table object from python-docx
            
        Returns:
            Dictionary with table data
        """
        table_data = []
        
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                row_data.append(cell.text)
            table_data.append(row_data)
        
        return {
            "data": table_data,
            "rows": len(table_data),
            "columns": len(table_data[0]) if table_data else 0,
            "extracted_text": ""
        }
    
    @staticmethod
    def _table_to_text(table_data: List[List[str]]) -> str:
        """Convert table to text format."""
        text_rows = []
        for row in table_data:
            row_text = " | ".join(str(cell) if cell else "" for cell in row)
            text_rows.append(row_text)
        return "\n".join(text_rows)
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted text."""
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
    
    @staticmethod
    def _estimate_page_count(text_length: int) -> int:
        """Estimate page count based on text length."""
        # Rough estimate: ~3000 characters per page
        return max(1, text_length // 3000)
