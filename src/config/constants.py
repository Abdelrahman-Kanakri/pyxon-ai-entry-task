"""
Application Constants

Central location for all application-wide constants and enumerations.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

from enum import Enum
from typing import Dict, List


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    XLSX = "xlsx"


class ChunkingStrategy(str, Enum):
    """Chunking strategy types."""
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    SEMANTIC = "semantic"


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    ARABIC = "ar"
    MIXED = "mixed"


class Entity_Type(str, Enum):
    """Named Entity Recognition types."""
    PERSON = "PERSON"
    LOCATION = "LOCATION"
    ORGANIZATION = "ORG"
    DATE = "DATE"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    FACILITY = "FAC"
    PRODUCT = "PRODUCT"


class RetrievalStrategy(str, Enum):
    """Retrieval strategy types."""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    GRAPH = "graph"


class Environment(str, Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


# Default chunk sizes in tokens
DEFAULT_CHUNK_SIZES: Dict[DocumentType, int] = {
    DocumentType.PDF: 512,
    DocumentType.DOCX: 512,
    DocumentType.TXT: 512,
    DocumentType.XLSX: 256,
}

# Default chunk overlap
DEFAULT_CHUNK_OVERLAP = 50

# Supported file extensions
SUPPORTED_EXTENSIONS: Dict[DocumentType, List[str]] = {
    DocumentType.PDF: [".pdf"],
    DocumentType.DOCX: [".docx"],
    DocumentType.DOC: [".doc"],
    DocumentType.TXT: [".txt"],
    DocumentType.XLSX: [".xlsx", ".xls"],
}

# Maximum file sizes in MB
MAX_FILE_SIZES: Dict[DocumentType, int] = {
    DocumentType.PDF: 50,
    DocumentType.DOCX: 50,
    DocumentType.DOC: 50,
    DocumentType.TXT: 100,
    DocumentType.XLSX: 30,
}

# Embedding dimensions for different models
EMBEDDING_DIMENSIONS: Dict[str, int] = {
    "sentence-transformers/multilingual-e5-small": 384,
    "sentence-transformers/multilingual-e5-base": 768,
    "sentence-transformers/multilingual-e5-large": 1024,
}

# Arabic special characters and diacritics
ARABIC_DIACRITICS = {
    "FATHA": "\u064E",
    "DAMMA": "\u064F",
    "KASRA": "\u0650",
    "SHADDA": "\u0651",
    "SUKUN": "\u0652",
    "TANWIN_FATHA": "\u064B",
    "TANWIN_DAMMA": "\u064D",
    "TANWIN_KASRA": "\u064C",
}

# Retrieval parameters
DEFAULT_TOP_K = 5
DEFAULT_RERANKING_THRESHOLD = 0.5

# Timeout values in seconds
DEFAULT_TIMEOUT = 30
OCR_TIMEOUT = 120
LLM_TIMEOUT = 60

# API response status codes
SUCCESS_CODES = {200, 201}
CLIENT_ERROR_CODES = {400, 401, 403, 404, 422}
SERVER_ERROR_CODES = {500, 502, 503}

# Logging formats
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

# Cache TTL values in seconds
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 3600  # 1 hour
CACHE_TTL_LONG = 86400  # 24 hours

# Benchmark metrics
BENCHMARK_METRICS = [
    "retrieval_accuracy",
    "chunking_quality",
    "parsing_speed",
    "embedding_time",
    "retrieval_latency",
    "arabic_correctness",
]
