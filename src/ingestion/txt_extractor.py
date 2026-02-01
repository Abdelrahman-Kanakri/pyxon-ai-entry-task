"""
Text File Extractor

Handles extraction from plain text files with encoding detection.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import time
import logging
from typing import Dict, Optional, Any
from pathlib import Path

# Optional import for encoding detection
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

from .base import BaseExtractor, ExtractedContent, ExtractionMetadata, ExtractionStatus

logger = logging.getLogger(__name__)


class TXTExtractor(BaseExtractor):
    """Extract content from TXT files."""
    
    def _is_supported_format(self) -> bool:
        """Check if file is a TXT."""
        return self.file_path.suffix.lower() == ".txt"
    
    def extract(self) -> ExtractedContent:
        """
        Extract content from TXT file.
        
        Returns:
            ExtractedContent: Extracted text and metadata
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            # Detect encoding
            encoding = self._detect_encoding()
            
            # Read file
            with open(self.file_path, "r", encoding=encoding, errors="replace") as f:
                raw_text = f.read()
            
            # Clean text
            cleaned_text = self._clean_text(raw_text)
            
            # Detect language
            language = self._detect_language(cleaned_text)
            
            # Extract structure (paragraphs, sections)
            structured_data = self._extract_structure(cleaned_text)
            
            # Calculate confidence
            confidence = min(len(cleaned_text) / 1000, 1.0)
            
            # Estimate page count
            page_count = self._estimate_page_count(len(raw_text))
            
            extraction_time = time.time() - start_time
            
            return ExtractedContent(
                raw_text=raw_text,
                cleaned_text=cleaned_text,
                structured_data=structured_data,
                language=language,
                page_count=page_count,
                extracted_tables=[],
                images_extracted=0,
                extraction_confidence=confidence,
                metadata={
                    "extraction_time": extraction_time,
                    "file_size": self.get_file_size(),
                    "encoding": encoding,
                    "line_count": len(cleaned_text.split("\n")),
                    "word_count": len(cleaned_text.split())
                },
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"TXT extraction failed: {str(e)}")
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
        encoding = self._detect_encoding()
        extraction_time = time.time() - start_time
        
        return ExtractionMetadata(
            source_file=str(self.file_path),
            extraction_time=extraction_time,
            file_size_bytes=self.get_file_size(),
            encoder_used=encoding,
            status=ExtractionStatus.SUCCESS
        )
    
    def get_file_encoding(self) -> str:
        """Detect and return file encoding."""
        return self._detect_encoding()
    
    def _detect_encoding(self) -> str:
        """
        Detect file encoding using chardet.
        
        Returns:
            Encoding name (e.g., 'utf-8', 'arabic', 'cp1252')
        """
        try:
            with open(self.file_path, "rb") as f:
                raw_data = f.read()
            
            detected = chardet.detect(raw_data)
            
            if detected and detected.get("encoding"):
                encoding = detected["encoding"]
                confidence = detected.get("confidence", 0)
                
                if confidence > 0.7:
                    return encoding
        except Exception as e:
            logger.warning(f"Encoding detection failed: {e}")
        
        # Fallback to UTF-8
        return "utf-8"
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean extracted text.
        
        - Remove excessive blank lines
        - Normalize whitespace
        - Remove control characters
        """
        # Remove null characters
        text = text.replace("\x00", "")
        
        # Normalize line endings
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        
        # Remove excessive blank lines
        lines = text.split("\n")
        cleaned_lines = []
        blank_count = 0
        
        for line in lines:
            stripped = line.rstrip()
            
            if not stripped:
                blank_count += 1
                if blank_count <= 1:  # Allow max 1 blank line
                    cleaned_lines.append("")
            else:
                blank_count = 0
                cleaned_lines.append(stripped)
        
        return "\n".join(cleaned_lines).strip()
    
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
    def _extract_structure(text: str) -> Dict[str, Any]:
        """
        Extract document structure from text.
        
        Identifies paragraphs, potential headings, etc.
        """
        paragraphs = []
        current_paragraph = []
        
        for line in text.split("\n"):
            if not line.strip():
                # Empty line marks paragraph boundary
                if current_paragraph:
                    paragraphs.append("\n".join(current_paragraph))
                    current_paragraph = []
            else:
                current_paragraph.append(line)
        
        # Add final paragraph
        if current_paragraph:
            paragraphs.append("\n".join(current_paragraph))
        
        return {
            "paragraph_count": len(paragraphs),
            "paragraphs": paragraphs[:10],  # First 10 for preview
            "line_count": len(text.split("\n")),
            "word_count": len(text.split())
        }
    
    @staticmethod
    def _estimate_page_count(text_length: int) -> int:
        """Estimate page count based on text length."""
        # Rough estimate: ~3000 characters per page
        return max(1, text_length // 3000)
