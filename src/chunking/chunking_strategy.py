"""
Chunking Strategy

Base classes and interfaces for document chunking strategies.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ChunkType(Enum):
    """Types of chunks."""

    TEXT = "text"
    TABLE = "table"
    CODE = "code"
    HEADING = "heading"


@dataclass
class Chunk:
    """Represents a document chunk."""

    content: str
    chunk_id: str
    chunk_index: int
    chunk_type: ChunkType
    metadata: Dict[str, Any]
    start_pos: int
    end_pos: int
    tokens: Optional[int] = None

    def __post_init__(self):
        """Estimate token count if not provided."""
        if self.tokens is None:
            # Rough estimate: ~4 characters per token
            self.tokens = len(self.content) // 4


class ChunkingStrategy(ABC):
    """
    Abstract base class for chunking strategies.

    Defines the interface that all chunking strategies must implement.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize the chunking strategy.

        Args:
            chunk_size: Target size for chunks (in tokens)
            chunk_overlap: Overlap between chunks (in tokens)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def chunk_text(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Chunk text into segments.

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of Chunk objects
        """
        pass

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token
        # More accurate would use tiktoken, but this is good enough
        return len(text) // 4

    def _create_chunk(
        self,
        content: str,
        index: int,
        start_pos: int,
        end_pos: int,
        chunk_type: ChunkType = ChunkType.TEXT,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Chunk:
        """
        Create a chunk object.

        Args:
            content: Chunk content
            index: Chunk index
            start_pos: Start position in original text
            end_pos: End position in original text
            chunk_type: Type of chunk
            metadata: Additional metadata

        Returns:
            Chunk object
        """
        chunk_id = f"chunk_{index:04d}"
        tokens = self._estimate_tokens(content)

        chunk_metadata = metadata or {}
        chunk_metadata.update(
            {"chunk_size": len(content), "tokens": tokens, "type": chunk_type.value}
        )

        return Chunk(
            content=content,
            chunk_id=chunk_id,
            chunk_index=index,
            chunk_type=chunk_type,
            metadata=chunk_metadata,
            start_pos=start_pos,
            end_pos=end_pos,
            tokens=tokens,
        )

    def _split_by_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        import re

        # Simple sentence splitting (can be improved with NLP)
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _split_by_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.

        Args:
            text: Text to split

        Returns:
            List of paragraphs
        """
        paragraphs = text.split("\n\n")
        return [p.strip() for p in paragraphs if p.strip()]
