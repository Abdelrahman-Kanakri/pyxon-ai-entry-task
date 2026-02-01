"""
Chunk Validator

Validates chunk quality and coherence.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from .chunking_strategy import Chunk

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of chunk validation."""

    is_valid: bool
    quality_score: float
    issues: List[str]
    warnings: List[str]


class ChunkValidator:
    """
    Validates chunk quality.

    Checks for coherence, completeness, and optimal sizing.
    """

    def __init__(
        self,
        min_chunk_size: int = 50,
        max_chunk_size: int = 2000,
        min_quality_score: float = 0.5,
    ):
        """
        Initialize chunk validator.

        Args:
            min_chunk_size: Minimum acceptable chunk size (chars)
            max_chunk_size: Maximum acceptable chunk size (chars)
            min_quality_score: Minimum quality score threshold
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.min_quality_score = min_quality_score
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate_chunk(self, chunk: Chunk) -> ValidationResult:
        """
        Validate a single chunk.

        Args:
            chunk: Chunk to validate

        Returns:
            ValidationResult
        """
        issues = []
        warnings = []

        # Check size
        chunk_size = len(chunk.content)

        if chunk_size < self.min_chunk_size:
            issues.append(f"Chunk too small: {chunk_size} < {self.min_chunk_size}")
        elif chunk_size > self.max_chunk_size:
            warnings.append(f"Chunk large: {chunk_size} > {self.max_chunk_size}")

        # Check content quality
        if not chunk.content.strip():
            issues.append("Chunk is empty or whitespace only")

        # Check for incomplete sentences
        if not chunk.content.rstrip().endswith((".", "!", "?", "\n", '"', "'")):
            warnings.append("Chunk may end mid-sentence")

        # Calculate quality score
        quality_score = self._calculate_quality_score(chunk)

        if quality_score < self.min_quality_score:
            warnings.append(f"Low quality score: {quality_score:.2f}")

        is_valid = len(issues) == 0

        return ValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            issues=issues,
            warnings=warnings,
        )

    def validate_chunks(self, chunks: List[Chunk]) -> Dict[str, Any]:
        """
        Validate a list of chunks.

        Args:
            chunks: List of chunks

        Returns:
            Dictionary with validation results
        """
        self.logger.info(f"Validating {len(chunks)} chunks")

        results = []
        total_valid = 0
        total_warnings = 0
        quality_scores = []

        for chunk in chunks:
            result = self.validate_chunk(chunk)
            results.append(result)

            if result.is_valid:
                total_valid += 1

            total_warnings += len(result.warnings)
            quality_scores.append(result.quality_score)

        avg_quality = (
            sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        )

        validation_summary = {
            "total_chunks": len(chunks),
            "valid_chunks": total_valid,
            "invalid_chunks": len(chunks) - total_valid,
            "total_warnings": total_warnings,
            "average_quality_score": avg_quality,
            "results": results,
        }

        self.logger.info(
            f"Validation complete: {total_valid}/{len(chunks)} valid, "
            f"avg quality: {avg_quality:.2f}"
        )

        return validation_summary

    def _calculate_quality_score(self, chunk: Chunk) -> float:
        """
        Calculate quality score for a chunk.

        Args:
            chunk: Chunk to score

        Returns:
            Quality score (0.0 to 1.0)
        """
        scores = []

        # Factor 1: Size appropriateness (0.0 - 1.0)
        chunk_size = len(chunk.content)
        ideal_size = (self.min_chunk_size + self.max_chunk_size) / 2
        size_diff = abs(chunk_size - ideal_size)
        size_score = max(0.0, 1.0 - (size_diff / ideal_size))
        scores.append(size_score)

        # Factor 2: Content completeness (0.0 - 1.0)
        has_start = (
            chunk.content.lstrip()[0].isupper() if chunk.content.strip() else False
        )
        has_end = chunk.content.rstrip().endswith((".", "!", "?", "\n"))
        completeness_score = (int(has_start) + int(has_end)) / 2.0
        scores.append(completeness_score)

        # Factor 3: Text density (not too sparse)
        words = chunk.content.split()
        if words:
            avg_word_length = sum(len(w) for w in words) / len(words)
            density_score = min(
                1.0, avg_word_length / 5.0
            )  # Normalize to ~5 chars/word
            scores.append(density_score)
        else:
            scores.append(0.0)

        # Average all scores
        return sum(scores) / len(scores)
