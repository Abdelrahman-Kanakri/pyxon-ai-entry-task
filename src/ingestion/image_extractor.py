"""
Image Extractor

Extracts text from images using OCR (Tesseract).

Author: Abdelrahman Kanakri
Date: 2026-02-01
Version: 1.1.0
"""

import logging
import pytesseract
import os
from PIL import Image
from pathlib import Path

from .base import BaseExtractor, ExtractedContent, ExtractionMetadata, ExtractionStatus


class ImageExtractor(BaseExtractor):
    """
    Extracts text from images using OCR.
    Handles English and Arabic scripts.
    """

    def __init__(self, file_path: str):
        """Initialize image extractor."""
        super().__init__(file_path)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Auto-configure Tesseract path for Windows if not in PATH
        if os.name == "nt":
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    self.logger.info(f"Set Tesseract path to: {path}")
                    break

    def _is_supported_format(self) -> bool:
        """Check if file format is supported."""
        return self.file_path.suffix.lower() in {
            ".png",
            ".jpg",
            ".jpeg",
            ".tiff",
            ".bmp",
        }

    def get_metadata(self) -> ExtractionMetadata:
        """Get extraction metadata."""
        return ExtractionMetadata(
            source_file=self.file_path.name,
            extraction_time=0.0,
            file_size_bytes=self.file_path.stat().st_size,
            encoder_used="tesseract",
            status=ExtractionStatus.SUCCESS,
        )

    def extract(self) -> ExtractedContent:
        """
        Extract content from image file.

        Returns:
            ExtractedContent with OCR text (Supports English + Arabic)
        """
        try:
            image = Image.open(self.file_path)

            # Extract text using Tesseract (multilingual support)
            custom_config = r"--oem 3 --psm 3"
            text = pytesseract.image_to_string(
                image, lang="eng+ara", config=custom_config
            )

            # Retry with different PSM if empty (often helps with screenshots)
            if not text.strip():
                self.logger.info(
                    "Default OCR empty, retrying with PSM 6 (Sparse text)..."
                )
                custom_config = r"--oem 3 --psm 6"
                text = pytesseract.image_to_string(
                    image, lang="eng+ara", config=custom_config
                )

            self.logger.info(f"OCR Extracted {len(text)} characters")

            # Basic metadata
            metadata = {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "ocr_length": len(text),
            }

            # Prepend context to help retrieval
            header = f"Context: Image content from file '{self.file_path.name}'\n"
            content_text = header + text

            return ExtractedContent(
                raw_text=content_text,
                cleaned_text=self._clean_text(content_text),
                metadata=metadata,
                page_count=1,
                structured_data={},  # Required field
                language="en",  # Default assumption
                extracted_tables=[],  # Required field
                images_extracted=0,  # Required field
                extraction_confidence=0.8 if text.strip() else 0.1,
                errors=[],  # Required field
                warnings=["OCR yielded no text"] if not text.strip() else [],
            )

        except ImportError:
            self.logger.error("pytesseract or Pillow not installed")
            raise
        except pytesseract.TesseractNotFoundError:
            self.logger.error("Tesseract-OCR binary not found on system")
            raise Exception("Tesseract-OCR not found. Please install Tesseract.")
        except Exception as e:
            self.logger.error(f"Error extracting image: {e}")
            raise

    def _clean_text(self, text: str) -> str:
        """Basic text cleaning."""
        # Remove excessive whitespace
        return " ".join(text.split())


import os
