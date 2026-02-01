"""
Configuration Settings Module

This module manages all application settings using Pydantic Settings
for environment variable loading and validation.

Features:
- Automatic environment variable loading from .env
- Type validation for all settings
- Support for multiple environments (development, production)
- Secrets management (credentials, API keys)

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

from pydantic_settings import BaseSettings
from typing import Optional, Literal
import os
from pathlib import Path


class DatabaseSettings(BaseSettings):
    """Database configuration - SQLite for testing, PostgreSQL for production."""

    use_sqlite: bool = True  # Set to False for PostgreSQL
    sqlite_path: str = "./data/app.db"
    host: str = "localhost"
    port: int = 5432
    name: str = "pyxon_parser"
    user: str = "postgres"
    password: str = ""
    pool_size: int = 20
    max_overflow: int = 40
    echo: bool = False

    @property
    def url(self) -> str:
        """Generate SQLAlchemy database URL."""
        if self.use_sqlite:
            return f"sqlite:///{self.sqlite_path}"
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    class Config:
        env_prefix = "DB_"


class ChromaSettings(BaseSettings):
    """Chroma vector database configuration."""

    host: str = "localhost"
    port: int = 8000
    db_path: str = "./data/chroma_db"
    client_type: Literal["http", "persistent", "ephemeral"] = "persistent"

    class Config:
        env_prefix = "CHROMA_"


class EmbeddingSettings(BaseSettings):
    """Embedding model configuration."""

    model: str = "intfloat/multilingual-e5-small"  # Multilingual E5 model
    provider: Literal["sentence-transformers", "openai", "huggingface"] = (
        "sentence-transformers"
    )
    dimension: int = 384

    class Config:
        env_prefix = "EMBEDDING_"


class LLMSettings(BaseSettings):
    """LLM provider credentials and configurations."""

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.3
    openai_max_tokens: int = 2000

    # Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"

    # Mistral
    mistral_api_key: Optional[str] = None
    mistral_model: str = "mistral-large-latest"

    # Google GenAI
    google_genai_api_key: Optional[str] = None
    google_genai_model: str = "gemini-3-pro-preview"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": False,  # Allow both MISTRAL_API_KEY and mistral_api_key
    }


class LangSmithSettings(BaseSettings):
    """LangSmith monitoring configuration."""

    api_key: Optional[str] = None
    endpoint: str = "https://api.smith.langchain.com"
    tracing: bool = True
    project: str = "pyxon-document-parser"

    class Config:
        env_prefix = "LANGSMITH_"


class DocumentProcessingSettings(BaseSettings):
    """Document processing configuration."""

    chunk_size: int = 512
    chunk_overlap: int = 50

    # OCR settings
    ocr_enabled: bool = True
    tesseract_path: Optional[str] = None
    ocr_language: str = "ara+eng"

    # Upload limits
    max_upload_size_mb: int = 50
    allowed_file_types: str = "pdf,docx,txt,doc,xlsx"

    @property
    def allowed_extensions(self) -> list:
        """Get list of allowed file extensions."""
        return self.allowed_file_types.split(",")

    class Config:
        env_prefix = ""


class ArabicSettings(BaseSettings):
    """Arabic language support configuration."""

    support_enabled: bool = True
    normalize_diacritics: bool = True
    preserve_diacritics: bool = False
    model: str = "AraBERT"

    class Config:
        env_prefix = "ARABIC_"


class RetrievalSettings(BaseSettings):
    """Search and retrieval configuration."""

    top_k: int = 5
    enable_reranking: bool = True
    rerank_model: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384"
    strategy: Literal["hybrid", "semantic", "keyword"] = "hybrid"

    class Config:
        env_prefix = "RETRIEVAL_"


class RedisSettings(BaseSettings):
    """Redis cache configuration."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    enable_cache: bool = True

    @property
    def url(self) -> str:
        """Generate Redis connection URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"

    class Config:
        env_prefix = "REDIS_"


class APISettings(BaseSettings):
    """FastAPI and Streamlit configuration."""

    host: str = "0.0.0.0"
    port: int = 8000
    prefix: str = "/api/v1"

    # Streamlit
    streamlit_port: int = 8501
    streamlit_server_headless: bool = False

    class Config:
        env_prefix = ""


class PathSettings(BaseSettings):
    """Application path configuration."""

    documents: str = "./data/documents"
    uploads: str = "./data/uploads"
    benchmarks: str = "./data/benchmarks"
    sample_documents: str = "./benchmarks/sample_documents"
    logs: str = "./logs"

    def __init__(self, **data):
        super().__init__(**data)
        # Create directories if they don't exist
        Path(self.documents).mkdir(parents=True, exist_ok=True)
        Path(self.uploads).mkdir(parents=True, exist_ok=True)
        Path(self.benchmarks).mkdir(parents=True, exist_ok=True)
        Path(self.logs).mkdir(parents=True, exist_ok=True)

    class Config:
        env_prefix = ""


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    file: str = "./logs/app.log"
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5
    level: str = "INFO"

    class Config:
        env_prefix = "LOG_"


class BenchmarkSettings(BaseSettings):
    """Benchmark configuration."""

    enabled: bool = True
    sample_size: int = 100
    timeout: int = 300

    class Config:
        env_prefix = "BENCHMARK_"


class Settings(BaseSettings):
    """
    Main settings class that combines all configuration modules.

    Usage:
        settings = Settings()
        db_url = settings.database.url
        chroma_path = settings.chroma.db_path
    """

    # Application metadata
    app_name: str = "Pyxon AI Document Parser"
    app_version: str = "1.0.0"
    env: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    chroma: ChromaSettings = ChromaSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
    llm: LLMSettings = LLMSettings()
    langsmith: LangSmithSettings = LangSmithSettings()
    document_processing: DocumentProcessingSettings = DocumentProcessingSettings()
    arabic: ArabicSettings = ArabicSettings()
    retrieval: RetrievalSettings = RetrievalSettings()
    redis: RedisSettings = RedisSettings()
    api: APISettings = APISettings()
    paths: PathSettings = PathSettings()
    logging: LoggingSettings = LoggingSettings()
    benchmark: BenchmarkSettings = BenchmarkSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()
