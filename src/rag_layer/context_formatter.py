"""
Context Formatter

Formats retrieved context for LLM prompts.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ContextFormatter:
    """
    Formats retrieved chunks into LLM-ready context.
    """

    def format_context(
        self, chunks: List[Dict[str, Any]], max_tokens: int = 2000
    ) -> str:
        """
        Format chunks into context string.

        Args:
            chunks: Retrieved chunks
            max_tokens: Maximum context tokens

        Returns:
            Formatted context string
        """
        context_parts = []
        current_tokens = 0

        for i, chunk in enumerate(chunks):
            content = chunk.get("content", "")
            chunk_tokens = len(content) // 4  # Rough estimate

            if current_tokens + chunk_tokens > max_tokens:
                break

            context_parts.append(f"[{i+1}] {content}")
            current_tokens += chunk_tokens

        return "\n\n".join(context_parts)
