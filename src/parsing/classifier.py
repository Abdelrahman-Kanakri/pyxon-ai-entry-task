"""
Document Classifier

Analyzes documents to determine their type, structure complexity,
and recommends appropriate chunking strategies.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from src.ingestion.base import ExtractedContent
from src.config import constants

logger = logging.getLogger(__name__)


class DocumentComplexity(Enum):
    """Document complexity levels."""

    SIMPLE = "simple"  # Plain text, uniform structure
    MODERATE = "moderate"  # Some structure, mixed content
    COMPLEX = "complex"  # Rich structure, tables, images


class RecommendedStrategy(Enum):
    """Recommended chunking strategies."""

    FIXED = "fixed"  # Fixed-size chunks
    DYNAMIC = "dynamic"  # Content-aware dynamic chunks
    HYBRID = "hybrid"  # Combination of both


@dataclass
class DocumentClassification:
    """Result of document classification."""

    document_type: str
    complexity: DocumentComplexity
    has_tables: bool
    has_structure: bool
    has_images: bool
    language: str
    recommended_strategy: RecommendedStrategy
    confidence: float
    metadata: Dict[str, Any]


class DocumentClassifier:
    """
    Classifies documents and recommends processing strategies.

    Analyzes document structure, content type, and complexity to determine
    the optimal approach for chunking and processing.
    """

    def __init__(self):
        """Initialize the document classifier."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def classify_document(self, content: ExtractedContent) -> DocumentClassification:
        """
        Classify a document and recommend processing strategy.

        Args:
            content: Extracted document content

        Returns:
            DocumentClassification with analysis results
        """
        self.logger.info(f"Classifying document with {content.page_count} pages")

        # Analyze document features
        complexity = self._analyze_complexity(content)
        has_tables = len(content.extracted_tables) > 0
        has_structure = self._has_structural_elements(content)
        has_images = content.images_extracted > 0

        # Recommend strategy
        recommended_strategy = self._recommend_strategy(
            complexity=complexity,
            has_tables=has_tables,
            has_structure=has_structure,
            page_count=content.page_count,
        )

        # Calculate confidence
        confidence = self._calculate_confidence(content)

        # Build metadata
        metadata = {
            "page_count": content.page_count,
            "table_count": len(content.extracted_tables),
            "image_count": content.images_extracted,
            "text_length": len(content.cleaned_text),
            "extraction_confidence": content.extraction_confidence,
        }

        classification = DocumentClassification(
            document_type="text",  # Default type since file_type not in ExtractedContent
            complexity=complexity,
            has_tables=has_tables,
            has_structure=has_structure,
            has_images=has_images,
            language=content.language,
            recommended_strategy=recommended_strategy,
            confidence=confidence,
            metadata=metadata,
        )

        self.logger.info(
            f"Classification complete: {complexity.value} complexity, "
            f"strategy: {recommended_strategy.value}"
        )

        return classification

    def _analyze_complexity(self, content: ExtractedContent) -> DocumentComplexity:
        """
        Analyze document complexity based on structure and content.

        Args:
            content: Extracted document content

        Returns:
            DocumentComplexity level
        """
        complexity_score = 0

        # Factor 1: Tables
        if len(content.extracted_tables) > 0:
            complexity_score += 2
            if len(content.extracted_tables) > 3:
                complexity_score += 1

        # Factor 2: Images
        if content.images_extracted > 0:
            complexity_score += 1

        # Factor 3: Page count
        if content.page_count > 10:
            complexity_score += 1
        if content.page_count > 50:
            complexity_score += 1

        # Factor 4: Structured data
        structured_data = content.structured_data or {}
        if structured_data.get("headings"):
            complexity_score += 1
        if structured_data.get("sections"):
            complexity_score += 1

        # Classify based on score
        if complexity_score <= 2:
            return DocumentComplexity.SIMPLE
        elif complexity_score <= 4:
            return DocumentComplexity.MODERATE
        else:
            return DocumentComplexity.COMPLEX

    def _has_structural_elements(self, content: ExtractedContent) -> bool:
        """
        Check if document has structural elements like headings.

        Args:
            content: Extracted document content

        Returns:
            True if document has structure
        """
        structured_data = content.structured_data or {}

        return bool(
            structured_data.get("headings")
            or structured_data.get("sections")
            or structured_data.get("paragraphs_with_styles")
        )

    def _recommend_strategy(
        self,
        complexity: DocumentComplexity,
        has_tables: bool,
        has_structure: bool,
        page_count: int,
    ) -> RecommendedStrategy:
        """
        Recommend chunking strategy based on document features.

        Args:
            complexity: Document complexity level
            has_tables: Whether document has tables
            has_structure: Whether document has structural elements
            page_count: Number of pages

        Returns:
            Recommended chunking strategy
        """
        # Complex documents with structure -> Dynamic
        if complexity == DocumentComplexity.COMPLEX and has_structure:
            return RecommendedStrategy.DYNAMIC

        # Documents with tables but otherwise simple -> Hybrid
        if has_tables and complexity == DocumentComplexity.SIMPLE:
            return RecommendedStrategy.HYBRID

        # Large structured documents -> Dynamic
        if page_count > 20 and has_structure:
            return RecommendedStrategy.DYNAMIC

        # Simple, short documents -> Fixed
        if complexity == DocumentComplexity.SIMPLE and page_count < 10:
            return RecommendedStrategy.FIXED

        # Moderate complexity -> Hybrid
        if complexity == DocumentComplexity.MODERATE:
            return RecommendedStrategy.HYBRID

        # Default to dynamic for unknown cases
        return RecommendedStrategy.DYNAMIC

    def _calculate_confidence(self, content: ExtractedContent) -> float:
        """
        Calculate confidence score for classification.

        Args:
            content: Extracted document content

        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence_factors = []

        # Factor 1: Extraction confidence
        confidence_factors.append(content.extraction_confidence)

        # Factor 2: Text length (higher is better)
        text_length = len(content.cleaned_text)
        if text_length > 1000:
            confidence_factors.append(0.9)
        elif text_length > 500:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)

        # Factor 3: Language detection confidence
        if content.language and content.language != "unknown":
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)

        # Factor 4: Metadata completeness
        if content.metadata:
            metadata_score = len(content.metadata) / 10.0  # Normalize
            confidence_factors.append(min(metadata_score, 1.0))
        else:
            confidence_factors.append(0.3)

        # Average all factors
        return sum(confidence_factors) / len(confidence_factors)
