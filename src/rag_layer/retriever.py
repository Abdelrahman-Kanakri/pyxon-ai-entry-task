"""
Retriever

Performs hybrid search combining semantic and keyword-based retrieval.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any, Optional

from src.config.settings import Settings
from src.knowledge_store.embeddings import EmbeddingGenerator
from src.knowledge_store.vector_db import VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """
    Retrieves relevant chunks for queries using hybrid search.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize retriever."""
        self.settings = settings or Settings()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.embedding_generator = EmbeddingGenerator(settings)
        self.vector_store = VectorStore(settings)

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Query text
            top_k: Number of results (default from settings)
            filter_dict: Optional metadata filters

        Returns:
            List of retrieved chunks with scores
        """
        if top_k is None:
            top_k = self.settings.retrieval.top_k

        self.logger.info(f"Retrieving top {top_k} chunks for query")

        # Generate query embedding with E5 query prefix
        query_embedding = self.embedding_generator.generate_embedding(query, is_query=True)

        # Search vector store
        results = self.vector_store.search(
            query_embedding, top_k=top_k, filter_dict=filter_dict
        )

        # Format results
        retrieved_chunks = []
        for i, doc_id in enumerate(results["ids"]):
            chunk = {
                "id": doc_id,
                "content": results["documents"][i],
                "score": 1.0
                - results["distances"][i],  # Convert distance to similarity
                "metadata": (
                    results["metadatas"][i] if i < len(results["metadatas"]) else {}
                ),
            }
            retrieved_chunks.append(chunk)

        self.logger.info(f"Retrieved {len(retrieved_chunks)} chunks")
        return retrieved_chunks
