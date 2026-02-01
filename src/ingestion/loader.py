"""
Document Loader Factory

Factory pattern for creating appropriate extractor based on file type.
Handles document loading orchestration.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Union

from src.config import constants
from .base import BaseExtractor, ExtractedContent
from .pdf_extractor import PDFExtractor
from .docx_extractor import DOCXExtractor
from .txt_extractor import TXTExtractor
from .image_extractor import ImageExtractor

logger = logging.getLogger(__name__)


class DocumentLoader:
    """
    Orchestrates document loading and extraction.
    
    Uses factory pattern to create appropriate extractor based on file type.
    Handles errors gracefully and provides fallback options.
    """
    
    # Map file extensions to extractors
    EXTRACTORS = {
        ".pdf": PDFExtractor,
        ".docx": DOCXExtractor,
        ".doc": DOCXExtractor,
        ".txt": TXTExtractor,
        ".png": ImageExtractor,
        ".jpg": ImageExtractor,
        ".jpeg": ImageExtractor,
    }
    
    @staticmethod
    def load_document(file_path: Union[str, Path]) -> ExtractedContent:
        """
        Load and extract content from document.
        
        Args:
            file_path: Path to document file
            
        Returns:
            ExtractedContent: Extracted content and metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported
            Exception: If extraction fails
        """
        file_path = Path(file_path)
        
        logger.info(f"Loading document: {file_path}")
        
        # Validate file
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Get file extension
        extension = file_path.suffix.lower()
        
        # Check if format is supported
        if extension not in DocumentLoader.EXTRACTORS:
            supported = ", ".join(DocumentLoader.EXTRACTORS.keys())
            raise ValueError(
                f"Unsupported file format '{extension}'. "
                f"Supported formats: {supported}"
            )
        
        # Create appropriate extractor
        extractor_class = DocumentLoader.EXTRACTORS[extension]
        
        try:
            extractor = extractor_class(str(file_path))
            logger.info(f"Extracting content from {extension} file")
            content = extractor.extract()
            
            logger.info(
                f"Successfully extracted {content.page_count} pages, "
                f"{len(content.cleaned_text)} characters"
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to extract document: {str(e)}")
            raise
    
    @staticmethod
    def validate_file(file_path: Union[str, Path]) -> bool:
        """
        Validate that file is supported and readable.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is valid, False otherwise
        """
        file_path = Path(file_path)
        
        # Check existence
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return False
        
        # Check if it's a file
        if not file_path.is_file():
            logger.warning(f"Path is not a file: {file_path}")
            return False
        
        # Check file size
        file_size = file_path.stat().st_size
        extension = file_path.suffix.lower()
        
        if extension in constants.MAX_FILE_SIZES:
            max_size_bytes = constants.MAX_FILE_SIZES.get(
                constants.DocumentType(extension[1:]),
                50
            ) * 1024 * 1024  # Convert MB to bytes
            
            if file_size > max_size_bytes:
                logger.warning(
                    f"File size ({file_size} bytes) exceeds limit "
                    f"({max_size_bytes} bytes)"
                )
                return False
        
        # Check file extension
        if extension not in DocumentLoader.EXTRACTORS:
            logger.warning(f"Unsupported file format: {extension}")
            return False
        
        return True
    
    @staticmethod
    def get_supported_formats() -> list:
        """Get list of supported file formats."""
        return list(DocumentLoader.EXTRACTORS.keys())
    
    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> dict:
        """
        Get information about file without full extraction.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        file_path = Path(file_path)
        
        return {
            "name": file_path.name,
            "extension": file_path.suffix.lower(),
            "size_bytes": file_path.stat().st_size,
            "size_mb": round(file_path.stat().st_size / 1024 / 1024, 2),
            "path": str(file_path),
            "supported": file_path.suffix.lower() in DocumentLoader.EXTRACTORS,
            "created": file_path.stat().st_ctime,
            "modified": file_path.stat().st_mtime,
        }
