"""
Chunking Module

Provides document chunking strategies including fixed-size and
dynamic content-aware chunking.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

from .chunking_strategy import ChunkingStrategy, Chunk, ChunkType
from .fixed_chunker import FixedChunker
from .dynamic_chunker import DynamicChunker
from .chunk_validator import ChunkValidator, ValidationResult

__all__ = [
    "ChunkingStrategy",
    "Chunk",
    "ChunkType",
    "FixedChunker",
    "DynamicChunker",
    "ChunkValidator",
    "ValidationResult",
]
