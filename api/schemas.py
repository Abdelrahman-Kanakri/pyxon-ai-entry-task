"""
API Schemas

Pydantic models for request and response validation.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# Health Check Schemas
class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str


# Document Parsing Schemas
class DocumentUploadResponse(BaseModel):
    """Document upload response."""

    document_id: str
    filename: str
    status: str
    chunk_count: int
    message: str


class DocumentInfo(BaseModel):
    """Document information."""

    id: str
    filename: str
    file_type: str
    page_count: int
    upload_date: str
    language: Optional[str] = None


class DocumentListResponse(BaseModel):
    """List of documents response."""

    documents: List[DocumentInfo]
    total: int


# Retrieval Schemas
class QueryRequest(BaseModel):
    """Query request."""

    query: str = Field(..., description="Query text")
    top_k: int = Field(5, description="Number of results", ge=1, le=20)
    document_id: Optional[str] = Field(None, description="Filter by document ID")


class ChunkResult(BaseModel):
    """Retrieved chunk result."""

    content: str
    score: float
    metadata: Dict[str, Any]


class QueryResponse(BaseModel):
    """Query response."""

    query: str
    chunks: List[ChunkResult]
    total_results: int
    answer: Optional[str] = None
