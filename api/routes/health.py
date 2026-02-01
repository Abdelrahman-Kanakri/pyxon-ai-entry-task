"""
Health Check Routes

System health and status endpoints.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

from fastapi import APIRouter
from datetime import datetime

from ..schemas import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(status="healthy", timestamp=datetime.utcnow().isoformat())


@router.get("/db", response_model=dict)
async def health_check_db():
    """Database connection health check."""
    try:
        from src.knowledge_store.sql_db import SQLStore

        sql_store = SQLStore()
        session = sql_store.get_session()
        session.close()

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
