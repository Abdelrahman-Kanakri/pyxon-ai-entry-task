"""
RAG Document Processing Pipeline

A comprehensive document ingestion and RAG (Retrieval-Augmented Generation) system
supporting multiple file formats with intelligent chunking, semantic analysis,
and vector-based retrieval.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Junior Developer"

# Configuration
from .config import (
    settings,
    Settings,
    DocumentType,
    ChunkingStrategy,
    Language,
    Entity_Type,
    RetrievalStrategy,
    Environment,
)

# Ingestion - Document loading and extraction
from .ingestion import (
    DocumentLoader,
    BaseExtractor,
    PDFExtractor,
    DOCXExtractor,
    TXTExtractor,
    ExtractedContent,
    ExtractionMetadata,
    ExtractionStatus,
)

# Parsing - Document analysis and understanding
from .parsing import (
    DocumentClassifier,
    DocumentClassification,
    DocumentComplexity,
    StructuralExtractor,
    DocumentStructure,
    SemanticExtractor,
    SemanticAnalysis,
    LLMInterpreter,
    LLMInterpretation,
)

# Chunking - Document splitting strategies
from .chunking import (
    ChunkingStrategy as ChunkingStrategyBase,
    Chunk,
    ChunkType,
    FixedChunker,
    DynamicChunker,
    ChunkValidator,
    ValidationResult,
)

# Knowledge Store - Embeddings and storage
from .knowledge_store import (
    EmbeddingGenerator,
    VectorStore,
    SQLStore,
    Document,
    ChunkRecord,
    Indexer,
)

# RAG Layer - Retrieval and context
from .rag_layer import (
    Retriever,
    Reranker,
    ContextFormatter,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Config
    "settings",
    "Settings",
    "DocumentType",
    "ChunkingStrategy",
    "Language",
    "Entity_Type",
    "RetrievalStrategy",
    "Environment",
    # Ingestion
    "DocumentLoader",
    "BaseExtractor",
    "PDFExtractor",
    "DOCXExtractor",
    "TXTExtractor",
    "ExtractedContent",
    "ExtractionMetadata",
    "ExtractionStatus",
    # Parsing
    "DocumentClassifier",
    "DocumentClassification",
    "DocumentComplexity",
    "StructuralExtractor",
    "DocumentStructure",
    "SemanticExtractor",
    "SemanticAnalysis",
    "LLMInterpreter",
    "LLMInterpretation",
    # Chunking
    "ChunkingStrategyBase",
    "Chunk",
    "ChunkType",
    "FixedChunker",
    "DynamicChunker",
    "ChunkValidator",
    "ValidationResult",
    # Knowledge Store
    "EmbeddingGenerator",
    "VectorStore",
    "SQLStore",
    "Document",
    "ChunkRecord",
    "Indexer",
    # RAG Layer
    "Retriever",
    "Reranker",
    "ContextFormatter",
]
