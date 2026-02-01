"""
Vector Database (Chroma)

Manages vector storage and similarity search using Chroma DB.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.config.settings import Settings
from src.chunking.chunking_strategy import Chunk

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector database interface using Chroma.

    Stores embeddings and performs similarity search.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize vector store.

        Args:
            settings: Application settings
        """
        self.settings = settings or Settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._client = None
        self._collection = None

    def _initialize_client(self):
        """Initialize Chroma client."""
        if self._client is not None:
            return

        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            # Create data directory if it doesn't exist
            chroma_path = Path(self.settings.chroma.db_path)
            chroma_path.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"Initializing Chroma DB at {chroma_path}")

            # Initialize persistent client
            self._client = chromadb.PersistentClient(path=str(chroma_path))

            self.logger.info("Chroma DB initialized successfully")

        except ImportError:
            self.logger.error("chromadb not installed")
            raise
        except Exception as e:
            self.logger.error(f"Error initializing Chroma: {e}")
            raise

    def get_or_create_collection(self, collection_name: str = "documents"):
        """
        Get or create a collection.

        Args:
            collection_name: Name of the collection
        """
        self._initialize_client()

        try:
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Document chunks with embeddings"},
            )

            self.logger.info(f"Using collection: {collection_name}")

        except Exception as e:
            self.logger.error(f"Error getting collection: {e}")
            raise

    def add_chunks(
        self, chunks: List[Chunk], embeddings: List[List[float]], document_id: str
    ):
        """
        Add chunks with embeddings to vector store.

        Args:
            chunks: List of chunks
            embeddings: List of embedding vectors
            document_id: Document identifier
        """
        if self._collection is None:
            self.get_or_create_collection()

        self.logger.info(f"Adding {len(chunks)} chunks to vector store")

        try:
            # Prepare data
            ids = [f"{document_id}_{chunk.chunk_id}" for chunk in chunks]
            documents = [chunk.content for chunk in chunks]
            metadatas = [
                {
                    "document_id": document_id,
                    "chunk_index": chunk.chunk_index,
                    "chunk_type": chunk.chunk_type.value,
                    "tokens": chunk.tokens,
                    **chunk.metadata,
                }
                for chunk in chunks
            ]

            # Add to collection
            self._collection.add(
                ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
            )

            self.logger.info(f"Successfully added {len(chunks)} chunks")

        except Exception as e:
            self.logger.error(f"Error adding chunks: {e}")
            raise

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Search for similar chunks.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            Dictionary with search results
        """
        if self._collection is None:
            self.get_or_create_collection()

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding], n_results=top_k, where=filter_dict
            )

            return {
                "ids": results["ids"][0] if results["ids"] else [],
                "documents": results["documents"][0] if results["documents"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            }

        except Exception as e:
            self.logger.error(f"Error searching: {e}")
            raise

    def delete_document(self, document_id: str):
        """
        Delete all chunks for a document.

        Args:
            document_id: Document identifier
        """
        if self._collection is None:
            self.get_or_create_collection()

        try:
            self._collection.delete(where={"document_id": document_id})

            self.logger.info(f"Deleted document: {document_id}")

        except Exception as e:
            self.logger.error(f"Error deleting document: {e}")
            raise

    def count(self) -> int:
        """
        Get total number of chunks in store.

        Returns:
            Number of chunks
        """
        if self._collection is None:
            self.get_or_create_collection()

        try:
            return self._collection.count()
        except Exception as e:
            self.logger.error(f"Error counting: {e}")
            return 0
