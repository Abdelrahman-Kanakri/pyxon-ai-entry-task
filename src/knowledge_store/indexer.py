"""
Indexer

Orchestrates storage across vector and SQL databases.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
import uuid
from typing import List, Dict, Any, Optional

from src.config.settings import Settings
from src.ingestion.base import ExtractedContent
from src.chunking.chunking_strategy import Chunk
from .embeddings import EmbeddingGenerator
from .vector_db import VectorStore
from .sql_db import SQLStore

logger = logging.getLogger(__name__)


class Indexer:
    """
    Coordinates document indexing across storage systems.

    Manages the complete pipeline: chunking → embedding → storage.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize indexer.

        Args:
            settings: Application settings
        """
        self.settings = settings or Settings()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize components
        self.embedding_generator = EmbeddingGenerator(settings)
        self.vector_store = VectorStore(settings)
        self.sql_store = SQLStore(settings)

    def index_document(
        self,
        content: ExtractedContent,
        chunks: List[Chunk],
        filename: str,
        document_id: Optional[str] = None,
    ) -> str:
        """
        Index a document with its chunks.

        Args:
            content: Extracted document content
            chunks: Document chunks
            filename: Original filename
            document_id: Optional document ID (generated if not provided)

        Returns:
            Document ID
        """
        # Generate document ID if not provided
        if document_id is None:
            document_id = str(uuid.uuid4())

        self.logger.info(f"Indexing document {document_id} with {len(chunks)} chunks")

        try:
            # Step 1: Generate embeddings for chunks
            embeddings = []
            if chunks:
                self.logger.info("Generating embeddings...")
                chunk_texts = [chunk.content for chunk in chunks]
                embeddings = self.embedding_generator.generate_embeddings_batch(
                    chunk_texts
                )

                # Step 2: Store in vector database
                self.logger.info("Storing in vector database...")
                self.vector_store.add_chunks(chunks, embeddings, document_id)
            else:
                self.logger.warning("No chunks to index. Skipping vector storage.")

            # Step 3: Store metadata in SQL database
            self.logger.info("Storing metadata in SQL database...")

            # Derive file_type from filename
            from pathlib import Path

            file_type = Path(filename).suffix.lower().lstrip(".")

            self.sql_store.add_document(
                document_id=document_id,
                filename=filename,
                file_type=file_type,
                file_size=(
                    content.metadata.get("file_size", 0) if content.metadata else 0
                ),
                page_count=content.page_count,
                language=content.language,
                metadata={
                    "extraction_confidence": content.extraction_confidence,
                    "extraction_method": (
                        content.metadata.get("extraction_method")
                        if content.metadata
                        else None
                    ),
                    "chunk_count": len(chunks),
                },
            )

            self.sql_store.add_chunks(chunks, document_id)

            self.logger.info(f"Document {document_id} indexed successfully")
            return document_id

        except Exception as e:
            self.logger.error(f"Error indexing document: {e}")
            # Attempt cleanup
            try:
                self.delete_document(document_id)
            except:
                pass
            raise

    def delete_document(self, document_id: str):
        """
        Delete a document from all storage systems.

        Args:
            document_id: Document identifier
        """
        self.logger.info(f"Deleting document {document_id}")

        try:
            # Delete from vector store
            self.vector_store.delete_document(document_id)

            # Delete from SQL store
            self.sql_store.delete_document(document_id)

            self.logger.info(f"Document {document_id} deleted successfully")

        except Exception as e:
            self.logger.error(f"Error deleting document: {e}")
            raise

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document metadata.

        Args:
            document_id: Document identifier

        Returns:
            Document metadata or None
        """
        return self.sql_store.get_document(document_id)

    def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all documents.

        Args:
            limit: Maximum number to return

        Returns:
            List of document metadata
        """
        return self.sql_store.list_documents(limit)
