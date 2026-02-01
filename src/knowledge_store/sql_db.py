"""
SQL Database Integration

Manages metadata storage in PostgreSQL.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Text,
    DateTime,
    Float,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from src.config.settings import Settings
from src.chunking.chunking_strategy import Chunk

logger = logging.getLogger(__name__)

Base = declarative_base()


class Document(Base):
    """Document metadata table."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_type = Column(String)
    file_size = Column(Integer)
    page_count = Column(Integer)
    language = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String)
    doc_metadata = Column(JSON)  # Renamed from 'metadata' (reserved in SQLAlchemy)


class ChunkRecord(Base):
    """Chunk metadata table."""

    __tablename__ = "chunks"

    id = Column(String, primary_key=True)
    document_id = Column(String, nullable=False)
    chunk_index = Column(Integer)
    content = Column(Text)
    chunk_type = Column(String)
    tokens = Column(Integer)
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    chunk_metadata = Column(JSON)  # Renamed from 'metadata'
    created_at = Column(DateTime, default=datetime.utcnow)


class SQLStore:
    """
    SQL database interface for metadata storage.

    Uses PostgreSQL to store document and chunk metadata.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize SQL store.

        Args:
            settings: Application settings
        """
        self.settings = settings or Settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._engine = None
        self._session_factory = None

    def _initialize_engine(self):
        """Initialize database engine."""
        if self._engine is not None:
            return

        try:
            database_url = self.settings.database.url

            self.logger.info(f"Initializing database connection: {database_url[:30]}...")

            # SQLite doesn't support connection pooling
            if self.settings.database.use_sqlite:
                self._engine = create_engine(
                    database_url,
                    echo=self.settings.database.echo,
                    connect_args={"check_same_thread": False}  # Required for SQLite
                )
            else:
                self._engine = create_engine(
                    database_url,
                    pool_size=self.settings.database.pool_size,
                    max_overflow=self.settings.database.max_overflow,
                    echo=self.settings.database.echo,
                )

            # Create tables
            Base.metadata.create_all(self._engine)

            # Create session factory
            self._session_factory = sessionmaker(bind=self._engine)

            self.logger.info("Database initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise

    def get_session(self) -> Session:
        """
        Get a database session.

        Returns:
            SQLAlchemy session
        """
        self._initialize_engine()
        return self._session_factory()

    def add_document(
        self,
        document_id: str,
        filename: str,
        file_type: str,
        file_size: int,
        page_count: int,
        language: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Add document metadata.

        Args:
            document_id: Document identifier
            filename: File name
            file_type: File type/extension
            file_size: File size in bytes
            page_count: Number of pages
            language: Document language
            metadata: Additional metadata
        """
        session = self.get_session()

        try:
            document = Document(
                id=document_id,
                filename=filename,
                file_type=file_type,
                file_size=file_size,
                page_count=page_count,
                language=language,
                processing_status="completed",
                doc_metadata=metadata or {},
            )

            session.add(document)
            session.commit()

            self.logger.info(f"Added document: {document_id}")

        except Exception as e:
            session.rollback()
            self.logger.error(f"Error adding document: {e}")
            raise
        finally:
            session.close()

    def add_chunks(self, chunks: List[Chunk], document_id: str):
        """
        Add chunk metadata.

        Args:
            chunks: List of chunks
            document_id: Document identifier
        """
        session = self.get_session()

        try:
            chunk_records = []

            for chunk in chunks:
                record = ChunkRecord(
                    id=f"{document_id}_{chunk.chunk_id}",
                    document_id=document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    chunk_type=chunk.chunk_type.value,
                    tokens=chunk.tokens,
                    start_pos=chunk.start_pos,
                    end_pos=chunk.end_pos,
                    chunk_metadata=chunk.metadata,
                )
                chunk_records.append(record)

            session.bulk_save_objects(chunk_records)
            session.commit()

            self.logger.info(f"Added {len(chunks)} chunks for document {document_id}")

        except Exception as e:
            session.rollback()
            self.logger.error(f"Error adding chunks: {e}")
            raise
        finally:
            session.close()

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document metadata.

        Args:
            document_id: Document identifier

        Returns:
            Document metadata or None
        """
        session = self.get_session()

        try:
            document = session.query(Document).filter_by(id=document_id).first()

            if document:
                return {
                    "id": document.id,
                    "filename": document.filename,
                    "file_type": document.file_type,
                    "file_size": document.file_size,
                    "page_count": document.page_count,
                    "language": document.language,
                    "upload_date": (
                        document.upload_date.isoformat()
                        if document.upload_date
                        else None
                    ),
                    "processing_status": document.processing_status,
                    "metadata": document.doc_metadata,
                }

            return None

        finally:
            session.close()

    def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all documents.

        Args:
            limit: Maximum number of documents to return

        Returns:
            List of document metadata
        """
        session = self.get_session()

        try:
            documents = session.query(Document).limit(limit).all()

            return [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "file_type": doc.file_type,
                    "upload_date": (
                        doc.upload_date.isoformat() if doc.upload_date else None
                    ),
                    "page_count": doc.page_count,
                    "language": doc.language,
                }
                for doc in documents
            ]

        finally:
            session.close()

    def delete_document(self, document_id: str):
        """
        Delete document and its chunks.

        Args:
            document_id: Document identifier
        """
        session = self.get_session()

        try:
            # Delete chunks
            session.query(ChunkRecord).filter_by(document_id=document_id).delete()

            # Delete document
            session.query(Document).filter_by(id=document_id).delete()

            session.commit()

            self.logger.info(f"Deleted document: {document_id}")

        except Exception as e:
            session.rollback()
            self.logger.error(f"Error deleting document: {e}")
            raise
        finally:
            session.close()
