"""
Configuration Module

Provides centralized configuration management for the entire application.
Includes settings validation, environment variable loading, and constants.

Example:
    from src.config import settings, constants
    
    db_url = settings.database.url
    max_size = constants.MAX_FILE_SIZES["pdf"]
"""

from .settings import Settings, settings
from .constants import (
    DocumentType,
    ChunkingStrategy,
    Language,
    Entity_Type,
    RetrievalStrategy,
    Environment,
)

__all__ = [
    "settings",
    "Settings",
    "DocumentType",
    "ChunkingStrategy",
    "Language",
    "Entity_Type",
    "RetrievalStrategy",
    "Environment",
]
