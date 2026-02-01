"""
Fixed Chunker

Implements fixed-size chunking with configurable overlap.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any, Optional

from .chunking_strategy import ChunkingStrategy, Chunk, ChunkType

logger = logging.getLogger(__name__)


class FixedChunker(ChunkingStrategy):
    """
    Fixed-size chunking strategy.

    Splits text into fixed-size chunks with optional overlap.
    Simple and predictable for uniform content.
    """

    def chunk_text(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Chunk text into fixed-size segments.

        Args:
            text: Text to chunk
            metadata: Optional metadata

        Returns:
            List of Chunk objects
        """
        self.logger.info(f"Chunking text with fixed strategy (size={self.chunk_size})")

        chunks = []

        # Convert token sizes to character estimates
        chunk_char_size = self.chunk_size * 4  # ~4 chars per token
        overlap_char_size = self.chunk_overlap * 4

        # Calculate step size (chunk size minus overlap)
        step_size = chunk_char_size - overlap_char_size

        # Create chunks
        start = 0
        index = 0

        while start < len(text):
            # Calculate end position
            end = min(start + chunk_char_size, len(text))

            # Extract chunk content
            chunk_content = text[start:end].strip()

            # Skip empty chunks
            if not chunk_content:
                break

            # Create chunk
            chunk = self._create_chunk(
                content=chunk_content,
                index=index,
                start_pos=start,
                end_pos=end,
                chunk_type=ChunkType.TEXT,
                metadata=metadata,
            )

            chunks.append(chunk)

            # Move to next chunk
            start += step_size
            index += 1

            # Break if we've reached the end
            if end >= len(text):
                break

        self.logger.info(f"Created {len(chunks)} fixed-size chunks")
        return chunks
