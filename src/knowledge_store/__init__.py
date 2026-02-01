"""
Knowledge Store Module

Manages embeddings generation and storage across vector and SQL databases.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

from .embeddings import EmbeddingGenerator
from .vector_db import VectorStore
from .sql_db import SQLStore, Document, ChunkRecord
from .indexer import Indexer

__all__ = [
    "EmbeddingGenerator",
    "VectorStore",
    "SQLStore",
    "Document",
    "ChunkRecord",
    "Indexer",
]
