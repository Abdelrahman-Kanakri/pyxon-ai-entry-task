"""
Semantic Extractor

Uses NLP to extract semantic information including topics,
key concepts, and named entities from documents.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass
from collections import Counter

from src.ingestion.base import ExtractedContent

logger = logging.getLogger(__name__)


@dataclass
class SemanticAnalysis:
    """Result of semantic content analysis."""

    topics: List[str]
    key_concepts: List[str]
    entities: Dict[str, List[str]]
    keywords: List[str]
    summary: Optional[str]
    language: str


class SemanticExtractor:
    """
    Extracts semantic information from documents using NLP.

    Identifies topics, key concepts, named entities, and generates
    summaries using natural language processing techniques.
    """

    def __init__(self):
        """Initialize the semantic extractor."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._nlp_model = None

    def _load_nlp_model(self, language: str = "en"):
        """
        Load appropriate NLP model based on language.

        Args:
            language: Document language code
        """
        if self._nlp_model is None:
            try:
                import spacy

                # Select model based on language
                if language.startswith("ar"):
                    # Arabic model
                    try:
                        self._nlp_model = spacy.load("xx_ent_wiki_sm")  # Multilingual
                        self.logger.info("Loaded multilingual NLP model for Arabic")
                    except OSError:
                        self.logger.warning(
                            "Multilingual model not available, using basic processing"
                        )
                        self._nlp_model = None
                else:
                    # English or other languages
                    try:
                        self._nlp_model = spacy.load("en_core_web_sm")
                        self.logger.info("Loaded English NLP model")
                    except OSError:
                        try:
                            self._nlp_model = spacy.load("xx_ent_wiki_sm")
                            self.logger.info("Loaded multilingual NLP model")
                        except OSError:
                            self.logger.warning(
                                "No NLP model available, using basic processing"
                            )
                            self._nlp_model = None

            except ImportError:
                self.logger.warning("spaCy not available, using basic processing")
                self._nlp_model = None

    def extract_semantics(self, content: ExtractedContent) -> SemanticAnalysis:
        """
        Extract semantic information from document content.

        Args:
            content: Extracted document content

        Returns:
            SemanticAnalysis with extracted information
        """
        self.logger.info("Extracting semantic information")

        # Load NLP model if needed
        self._load_nlp_model(content.language)

        # Extract various semantic elements
        if self._nlp_model:
            topics = self._extract_topics(content.cleaned_text)
            entities = self._extract_entities(content.cleaned_text)
            key_concepts = self._extract_key_concepts(content.cleaned_text)
        else:
            # Fallback to basic extraction
            topics = self._extract_topics_basic(content.cleaned_text)
            entities = {}
            key_concepts = self._extract_keywords_basic(content.cleaned_text)

        # Extract keywords
        keywords = self._extract_keywords(content.cleaned_text)

        # Generate summary (placeholder - would use summarization model)
        summary = self._generate_summary(content.cleaned_text)

        analysis = SemanticAnalysis(
            topics=topics,
            key_concepts=key_concepts,
            entities=entities,
            keywords=keywords,
            summary=summary,
            language=content.language,
        )

        self.logger.info(
            f"Semantic extraction complete: {len(topics)} topics, "
            f"{len(keywords)} keywords"
        )

        return analysis

    def _extract_topics(self, text: str) -> List[str]:
        """
        Extract main topics using NLP.

        Args:
            text: Document text

        Returns:
            List of identified topics
        """
        if not self._nlp_model:
            return self._extract_topics_basic(text)

        try:
            doc = self._nlp_model(text[:100000])  # Limit text length

            # Extract noun chunks as potential topics
            topics = []
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) >= 2:  # Multi-word topics
                    topics.append(chunk.text.lower())

            # Count and return most common
            topic_counts = Counter(topics)
            return [topic for topic, count in topic_counts.most_common(10)]

        except Exception as e:
            self.logger.error(f"Error extracting topics: {e}")
            return self._extract_topics_basic(text)

    def _extract_topics_basic(self, text: str) -> List[str]:
        """
        Basic topic extraction without NLP models.

        Args:
            text: Document text

        Returns:
            List of basic topics
        """
        # Simple capitalized phrase extraction
        import re

        # Find capitalized phrases (potential topics)
        pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b"
        matches = re.findall(pattern, text)

        # Count and return most common
        if matches:
            topic_counts = Counter(matches)
            return [topic for topic, count in topic_counts.most_common(10)]

        return []

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using NLP.

        Args:
            text: Document text

        Returns:
            Dictionary of entity types and their values
        """
        if not self._nlp_model:
            return {}

        try:
            doc = self._nlp_model(text[:100000])  # Limit text length

            entities = {
                "PERSON": [],
                "ORG": [],
                "GPE": [],  # Geopolitical entity
                "DATE": [],
                "MONEY": [],
            }

            for ent in doc.ents:
                if ent.label_ in entities:
                    entities[ent.label_].append(ent.text)

            # Deduplicate and limit
            for key in entities:
                entities[key] = list(set(entities[key]))[:10]

            return entities

        except Exception as e:
            self.logger.error(f"Error extracting entities: {e}")
            return {}

    def _extract_key_concepts(self, text: str) -> List[str]:
        """
        Extract key concepts using NLP.

        Args:
            text: Document text

        Returns:
            List of key concepts
        """
        if not self._nlp_model:
            return self._extract_keywords_basic(text)

        try:
            doc = self._nlp_model(text[:100000])

            # Extract important nouns and verbs
            key_concepts = []

            for token in doc:
                # Filter for important POS tags
                if token.pos_ in ["NOUN", "PROPN", "VERB"] and not token.is_stop:
                    if len(token.text) > 3:  # Skip short words
                        key_concepts.append(token.lemma_.lower())

            # Count and return most common
            concept_counts = Counter(key_concepts)
            return [concept for concept, count in concept_counts.most_common(15)]

        except Exception as e:
            self.logger.error(f"Error extracting key concepts: {e}")
            return self._extract_keywords_basic(text)

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.

        Args:
            text: Document text

        Returns:
            List of keywords
        """
        return self._extract_keywords_basic(text)

    def _extract_keywords_basic(self, text: str) -> List[str]:
        """
        Basic keyword extraction using word frequency.

        Args:
            text: Document text

        Returns:
            List of keywords
        """
        import re

        # Basic stopwords
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "this",
            "that",
            "these",
            "those",
            "it",
        }

        # Extract words
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())

        # Filter stopwords
        keywords = [w for w in words if w not in stopwords]

        # Count and return most common
        keyword_counts = Counter(keywords)
        return [keyword for keyword, count in keyword_counts.most_common(20)]

    def _generate_summary(self, text: str, max_length: int = 200) -> Optional[str]:
        """
        Generate a brief summary of the text.

        Args:
            text: Document text
            max_length: Maximum summary length

        Returns:
            Text summary or None
        """
        # Simple summary: first few sentences
        sentences = text.split(".")

        summary = ""
        for sentence in sentences[:3]:  # First 3 sentences
            sentence = sentence.strip()
            if sentence:
                summary += sentence + ". "
                if len(summary) >= max_length:
                    break

        return summary.strip() if summary else None
