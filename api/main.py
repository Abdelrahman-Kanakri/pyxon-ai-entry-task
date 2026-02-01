"""
FastAPI Main Application

Entry point for the document parser API.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import Settings
from .routes import health, parser, retrieval

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load settings
settings = Settings()

# Create FastAPI app
app = FastAPI(
    title="Pyxon AI Document Parser",
    description="AI-powered document parser with RAG capabilities",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    health.router, prefix=f"{settings.api.prefix}/health", tags=["Health"]
)
app.include_router(
    parser.router, prefix=f"{settings.api.prefix}/parse", tags=["Document Processing"]
)
app.include_router(
    retrieval.router, prefix=f"{settings.api.prefix}/retrieval", tags=["Retrieval"]
)

logger.info("FastAPI application initialized")
