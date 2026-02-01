"""
Dynamic Chunker

Implements content-aware dynamic chunking that respects semantic boundaries.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any, Optional

from .chunking_strategy import ChunkingStrategy, Chunk, ChunkType
from src.parsing.structural_extractor import Section

logger = logging.getLogger(__name__)


class DynamicChunker(ChunkingStrategy):
    """
    Dynamic chunking strategy.

    Adapts chunk boundaries to document structure and semantic units.
    Better for complex documents with clear organization.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        respect_structure: bool = True,
    ):
        """
        Initialize dynamic chunker.

        Args:
            chunk_size: Target chunk size
            chunk_overlap: Overlap between chunks
            respect_structure: Whether to respect document structure
        """
        super().__init__(chunk_size, chunk_overlap)
        self.respect_structure = respect_structure

    def chunk_text(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Chunk text dynamically based on content structure.

        Args:
            text: Text to chunk
            metadata: Optional metadata (can include sections)

        Returns:
            List of Chunk objects
        """
        self.logger.info("Chunking text with dynamic strategy")

        # Check if we have structural information
        sections = metadata.get("sections", []) if metadata else []

        if sections and self.respect_structure:
            chunks = self._chunk_by_structure(text, sections, metadata)
        else:
            chunks = self._chunk_by_semantics(text, metadata)

        self.logger.info(f"Created {len(chunks)} dynamic chunks")
        return chunks

    def _chunk_by_structure(
        self, text: str, sections: List[Section], metadata: Optional[Dict[str, Any]]
    ) -> List[Chunk]:
        """
        Chunk based on document structure.

        Args:
            text: Text to chunk
            sections: Document sections
            metadata: Metadata

        Returns:
            List of chunks
        """
        chunks = []
        chunk_index = 0

        for section in sections:
            # Extract section content
            section_content = text[section.start_pos : section.end_pos].strip()

            if not section_content:
                continue

            # Check if section fits in one chunk
            section_tokens = self._estimate_tokens(section_content)

            if section_tokens <= self.chunk_size:
                # Keep section as single chunk
                chunk = self._create_chunk(
                    content=section_content,
                    index=chunk_index,
                    start_pos=section.start_pos,
                    end_pos=section.end_pos,
                    chunk_type=ChunkType.TEXT,
                    metadata={
                        **(metadata or {}),
                        "section_title": section.title,
                        "section_level": section.level,
                    },
                )
                chunks.append(chunk)
                chunk_index += 1
            else:
                # Split large section into smaller chunks
                sub_chunks = self._split_large_section(
                    section_content,
                    section.start_pos,
                    chunk_index,
                    {
                        **(metadata or {}),
                        "section_title": section.title,
                        "section_level": section.level,
                    },
                )
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)

            # Process subsections recursively
            if section.subsections:
                subsection_chunks = self._chunk_by_structure(
                    text, section.subsections, metadata
                )
                # Update indices
                for chunk in subsection_chunks:
                    chunk.chunk_index = chunk_index
                    chunk.chunk_id = f"chunk_{chunk_index:04d}"
                    chunk_index += 1
                chunks.extend(subsection_chunks)

        return chunks

    def _chunk_by_semantics(
        self, text: str, metadata: Optional[Dict[str, Any]]
    ) -> List[Chunk]:
        """
        Chunk based on semantic boundaries (paragraphs, sentences).

        Args:
            text: Text to chunk
            metadata: Metadata

        Returns:
            List of chunks
        """
        chunks = []

        # Split by paragraphs first
        paragraphs = self._split_by_paragraphs(text)

        current_chunk = ""
        current_start = 0
        chunk_index = 0

        for para in paragraphs:
            para_tokens = self._estimate_tokens(para)
            current_tokens = self._estimate_tokens(current_chunk)

            # Check if adding this paragraph would exceed chunk size
            if current_tokens + para_tokens > self.chunk_size and current_chunk:
                # Create chunk from current content
                chunk = self._create_chunk(
                    content=current_chunk.strip(),
                    index=chunk_index,
                    start_pos=current_start,
                    end_pos=current_start + len(current_chunk),
                    chunk_type=ChunkType.TEXT,
                    metadata=metadata,
                )
                chunks.append(chunk)

                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + "\n\n" + para
                current_start += len(chunk.content) - len(overlap_text)
                chunk_index += 1
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_chunk(
                content=current_chunk.strip(),
                index=chunk_index,
                start_pos=current_start,
                end_pos=current_start + len(current_chunk),
                chunk_type=ChunkType.TEXT,
                metadata=metadata,
            )
            chunks.append(chunk)

        return chunks

    def _split_large_section(
        self, content: str, start_pos: int, start_index: int, metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """
        Split a large section into smaller chunks.

        Args:
            content: Section content
            start_pos: Start position
            start_index: Starting chunk index
            metadata: Metadata

        Returns:
            List of chunks
        """
        chunks = []
        sentences = self._split_by_sentences(content)

        current_chunk = ""
        chunk_index = start_index
        current_start = start_pos

        for sentence in sentences:
            sentence_tokens = self._estimate_tokens(sentence)
            current_tokens = self._estimate_tokens(current_chunk)

            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                # Create chunk
                chunk = self._create_chunk(
                    content=current_chunk.strip(),
                    index=chunk_index,
                    start_pos=current_start,
                    end_pos=current_start + len(current_chunk),
                    chunk_type=ChunkType.TEXT,
                    metadata=metadata,
                )
                chunks.append(chunk)

                # Start new chunk
                current_chunk = sentence + " "
                current_start += len(chunk.content)
                chunk_index += 1
            else:
                current_chunk += sentence + " "

        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_chunk(
                content=current_chunk.strip(),
                index=chunk_index,
                start_pos=current_start,
                end_pos=current_start + len(current_chunk),
                chunk_type=ChunkType.TEXT,
                metadata=metadata,
            )
            chunks.append(chunk)

        return chunks

    def _get_overlap_text(self, text: str) -> str:
        """
        Extract overlap text from end of chunk.

        Args:
            text: Chunk text

        Returns:
            Overlap text
        """
        overlap_char_size = self.chunk_overlap * 4

        if len(text) <= overlap_char_size:
            return text

        # Get last N characters, try to break at sentence boundary
        overlap = text[-overlap_char_size:]

        # Try to find last sentence boundary
        for delimiter in [". ", "! ", "? ", "\n"]:
            last_delim = overlap.rfind(delimiter)
            if last_delim > 0:
                return overlap[last_delim + len(delimiter) :]

        return overlap
