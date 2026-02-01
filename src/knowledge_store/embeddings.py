"""
Embeddings Generator

Generates vector embeddings for text using sentence transformers.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from typing import List, Optional, Dict, Any
import numpy as np

from src.config.settings import Settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings for text chunks.

    Uses sentence-transformers models to convert text into
    vector representations for semantic search.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize embedding generator.

        Args:
            settings: Application settings
        """
        self.settings = settings or Settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._model = None
        self._model_name = self.settings.embedding.model

    def _load_model(self):
        """

        Load embedding model."""
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer

            self.logger.info(f"Loading embedding model: {self._model_name}")
            self._model = SentenceTransformer(self._model_name)
            self.logger.info("Embedding model loaded successfully")

        except ImportError:
            self.logger.error("sentence-transformers not installed")
            raise
        except Exception as e:
            self.logger.error(f"Error loading embedding model: {e}")
            raise

    def generate_embedding(self, text: str, is_query: bool = False) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed
            is_query: If True, adds query prefix for E5 models

        Returns:
            Embedding vector as list of floats
        """
        self._load_model()

        try:
            # Add E5 prefix if using E5 model
            if "e5" in self._model_name.lower():
                prefix = "query: " if is_query else "passage: "
                text = prefix + text
            
            embedding = self._model.encode(
                text, 
                convert_to_numpy=True,
                normalize_embeddings=True  # Normalize for better similarity
            )
            return embedding.tolist()

        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 32, show_progress: bool = False, is_query: bool = False
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            is_query: If True, adds query prefix for E5 models

        Returns:
            List of embedding vectors
        """
        self._load_model()

        self.logger.info(f"Generating embeddings for {len(texts)} texts")

        try:
            # Add E5 prefix if using E5 model
            if "e5" in self._model_name.lower():
                prefix = "query: " if is_query else "passage: "
                texts = [prefix + text for text in texts]
            
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True,  # Normalize for better similarity
            )

            self.logger.info("Embeddings generated successfully")
            return [emb.tolist() for emb in embeddings]

        except Exception as e:
            self.logger.error(f"Error generating batch embeddings: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.

        Returns:
            Embedding dimension
        """
        self._load_model()
        return self._model.get_sentence_embedding_dimension()

    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (-1 to 1)
        """
        from numpy.linalg import norm

        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

        return float(similarity)
