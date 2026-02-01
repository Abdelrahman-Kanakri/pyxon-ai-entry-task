"""
Base Extractor Classes

Abstract base classes and interfaces for document extractors.
Defines the contract that all document extractors must implement.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum


class ExtractionStatus(str, Enum):
    """Status of extraction process."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class ExtractedContent:
    """Container for extracted document content."""
    
    raw_text: str
    """Complete raw text extracted from document."""
    
    cleaned_text: str
    """Processed and cleaned text."""
    
    structured_data: Dict[str, Any]
    """Structured metadata (headings, tables, etc.)."""
    
    language: str
    """Detected language (en, ar, mixed)."""
    
    page_count: int
    """Total number of pages."""
    
    extracted_tables: List[Dict[str, Any]]
    """Extracted tables with structure."""
    
    images_extracted: int
    """Number of images found."""
    
    extraction_confidence: float
    """Confidence score (0.0-1.0)."""
    
    metadata: Dict[str, Any]
    """Additional metadata (encoding, format, etc.)."""
    
    errors: List[str]
    """List of errors encountered during extraction."""
    
    warnings: List[str]
    """List of warnings during extraction."""


@dataclass
class ExtractionMetadata:
    """Metadata about extraction process."""
    
    source_file: str
    """Original file path/name."""
    
    extraction_time: float
    """Time taken for extraction in seconds."""
    
    file_size_bytes: int
    """Size of original file."""
    
    encoder_used: str
    """Encoding used for text extraction."""
    
    status: ExtractionStatus
    """Status of extraction."""


class BaseExtractor(ABC):
    """
    Abstract base class for all document extractors.
    
    Defines the interface that all extractors must implement.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize extractor.
        
        Args:
            file_path: Path to document file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported
        """
        self.file_path = Path(file_path)
        self._validate_file()
    
    def _validate_file(self) -> None:
        """Validate that file exists and is readable."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        if not self.file_path.is_file():
            raise ValueError(f"Path is not a file: {self.file_path}")
        
        if not self._is_supported_format():
            raise ValueError(f"Unsupported file format: {self.file_path.suffix}")
    
    @abstractmethod
    def _is_supported_format(self) -> bool:
        """Check if file format is supported by this extractor."""
        pass
    
    @abstractmethod
    def extract(self) -> ExtractedContent:
        """
        Extract content from document.
        
        Returns:
            ExtractedContent: Extracted content and metadata
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> ExtractionMetadata:
        """
        Get extraction metadata.
        
        Returns:
            ExtractionMetadata: Metadata about extraction
        """
        pass
    
    def get_file_size(self) -> int:
        """Get file size in bytes."""
        return self.file_path.stat().st_size
    
    def get_file_encoding(self) -> Optional[str]:
        """Detect file encoding (if applicable)."""
        # Default implementation
        return "utf-8"


class TextExtractor(BaseExtractor):
    """Base class for text-based extractors (PDF, DOCX, TXT)."""
    
    @abstractmethod
    def extract_text(self) -> str:
        """Extract plain text from document."""
        pass
    
    @abstractmethod
    def extract_structure(self) -> Dict[str, Any]:
        """
        Extract document structure (headings, sections, etc).
        
        Returns:
            Dict with structure information
        """
        pass


class ImageExtractor(BaseExtractor):
    """Base class for image-based extraction (scanned documents)."""
    
    @abstractmethod
    def extract_from_images(self) -> str:
        """
        Extract text from images using OCR.
        
        Returns:
            Extracted text from images
        """
        pass
    
    @abstractmethod
    def get_image_count(self) -> int:
        """Get total number of images in document."""
        pass
