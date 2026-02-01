"""
LLM Interpreter

Uses LLM to provide advanced document understanding including
content summarization and intent detection.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from src.config.settings import Settings
from src.ingestion.base import ExtractedContent

logger = logging.getLogger(__name__)


@dataclass
class LLMInterpretation:
    """Result of LLM-based document interpretation."""

    summary: str
    main_topics: list[str]
    document_purpose: str
    key_insights: list[str]
    suggested_tags: list[str]


class LLMInterpreter:
    """
    Uses LLM to provide advanced document understanding.

    Leverages large language models (Mistral or Google GenAI)
    to generate summaries, identify topics, and extract insights.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the LLM interpreter.

        Args:
            settings: Application settings (optional)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = settings or Settings()
        self._client = None

    def _initialize_client(self):
        """Initialize LLM client based on configuration."""
        if self._client is not None:
            return

        try:
            # Mistral AI
            if (
                self.settings.llm.mistral_api_key
                and self.settings.llm.mistral_api_key != "your_mistral_api_key"
            ):
                # Try v1.0+ SDK (Mistral)
                try:
                    from mistralai import Mistral
                    self._client = Mistral(api_key=self.settings.llm.mistral_api_key)
                    self._using_mistral_v1 = True
                    self.logger.info("Initialized Mistral AI client (v1+)")
                    return
                except ImportError:
                    pass

                # Try legacy SDK (MistralClient)
                try:
                    from mistralai.client import MistralClient
                    self._client = MistralClient(api_key=self.settings.llm.mistral_api_key)
                    self._using_mistral_v1 = False
                    self.logger.info("Initialized Mistral AI client (legacy)")
                    return
                except ImportError as e:
                    self.logger.warning(f"Could not import mistralai SDK: {e}")

            # Fallback to Google GenAI
            if self.settings.llm.google_genai_api_key:
                import google.generativeai as genai

                genai.configure(api_key=self.settings.llm.google_genai_api_key)
                self._client = genai
                self.logger.info("Initialized Google GenAI client")
            else:
                self.logger.warning("No LLM API key configured")

        except Exception as e:
            self.logger.error(f"Error initializing LLM client: {e}")
            self._client = None

    def interpret_document(
        self, content: ExtractedContent, max_length: int = 2000
    ) -> Optional[LLMInterpretation]:
        """
        Use LLM to interpret and understand document content.

        Args:
            content: Extracted document content
            max_length: Maximum text length to send to LLM

        Returns:
            LLMInterpretation or None if LLM not available
        """
        self.logger.info("Interpreting document with LLM")

        # Initialize client if needed
        self._initialize_client()

        if self._client is None:
            self.logger.warning("LLM client not available, skipping interpretation")
            return None

        # Truncate text if too long
        text = content.cleaned_text[:max_length]

        # Generate interpretation
        try:
            interpretation = self._generate_interpretation(text)
            self.logger.info("LLM interpretation complete")
            return interpretation

        except Exception as e:
            self.logger.error(f"Error during LLM interpretation: {e}")
            return None

    def _generate_interpretation(self, text: str) -> LLMInterpretation:
        """
        Generate interpretation using LLM.

        Args:
            text: Document text

        Returns:
            LLMInterpretation
        """
        # Create prompt
        prompt = f"""Analyze the following document and provide:
1. A brief summary (2-3 sentences)
2. Main topics (3-5 topics)
3. Document purpose (what is this document for?)
4. Key insights (3-5 important points)
5. Suggested tags for categorization (5-7 tags)

Document:
{text}

Respond in JSON format with keys: summary, main_topics, document_purpose, key_insights, suggested_tags"""

        # Call LLM
        response = self._call_llm(prompt)

        # Parse response
        return self._parse_response(response)

    def _call_llm(self, prompt: str) -> str:
        """
        Wrapper for LLM call that returns JSON fallback on error.
        Used by interpret_document().
        """
        try:
            return self._raw_llm_call(prompt)
        except Exception as e:
            self.logger.error(f"Error calling LLM (fallback used): {e}")
            return '{"summary": "Document analysis unavailable", "main_topics": [], "document_purpose": "Unknown", "key_insights": [], "suggested_tags": []}'

    def _raw_llm_call(self, prompt: str) -> str:
        """
        Direct call to LLM provider. Raises exceptions.
        Used by detect_language() and _call_llm().
        """
        # 1. Mistral AI (v1+)
        if getattr(self, "_using_mistral_v1", False):
            response = self._client.chat.complete(
                model=self.settings.llm.mistral_model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        # 2. Mistral AI (Legacy v0.x)
        # Check by class name or attribute presence
        elif hasattr(self._client, "chat") and not hasattr(self._client, "complete"):
            from mistralai.models.chat_completion import ChatMessage
            messages = [ChatMessage(role="user", content=prompt)]
            response = self._client.chat(
                model=self.settings.llm.mistral_model, messages=messages
            )
            return response.choices[0].message.content

        # 3. Google GenAI
        else:
            model = self._client.GenerativeModel(self.settings.llm.google_genai_model)
            response = model.generate_content(prompt)
            return response.text

    def _parse_response(self, response: str) -> LLMInterpretation:
        """
        Parse LLM response into structured format.

        Args:
            response: LLM response text

        Returns:
            LLMInterpretation
        """
        import json
        import re

        try:
            # Try to extract JSON from response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)

            return LLMInterpretation(
                summary=data.get("summary", ""),
                main_topics=data.get("main_topics", []),
                document_purpose=data.get("document_purpose", ""),
                key_insights=data.get("key_insights", []),
                suggested_tags=data.get("suggested_tags", []),
            )

        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {e}")
            # Return empty interpretation
            return LLMInterpretation(
                summary="Unable to parse LLM response",
                main_topics=[],
                document_purpose="Unknown",
                key_insights=[],
                suggested_tags=[],
            )

    def detect_language(self, text: str) -> str:
        """
        Detect language of text using LLM.

        Args:
            text: Text to analyze

        Returns:
            ISO 639-1 language code or "unknown"
        """
        self._initialize_client()

        if not self._client:
            return "unknown"

        # Take a representative sample (middle 1000 chars)
        start_idx = min(len(text) // 4, 1000)
        sample = text[start_idx : start_idx + 1000]
        
        prompt = f"""Identify the language of the following text. 
Respond ONLY with the ISO 639-1 language code (e.g., 'en', 'ar', 'fr').
If mixed, output the dominant language code.

Text:
{sample}"""

        try:
            response = self._raw_llm_call(prompt)
            # Clean response (remove quotes, extra whitespace)
            lang_code = response.strip().lower().replace('"', '').replace("'", "")
            # Validate length (should be 2 chars)
            if len(lang_code) > 2:
                lang_code = lang_code[:2]
            return lang_code
            
        except Exception as e:
            self.logger.error(f"Error detecting language with AI: {e}")
            print(f"DEBUG: LLM DETECT ERROR: {e}")
            return "unknown"

    def generate_answer(self, query: str, context: str) -> str:
        """
        Generate answer for RAG query.

        Args:
            query: User query
            context: Retrieved context

        Returns:
            Generated answer
        """
        self._initialize_client()

        if not self._client:
            return "LLM integration unavailable. Returning retrieved chunks only."

        prompt = f"""Based on the provided context, answer the user's question.
If the answer is not in the context, say "I cannot answer this based on the available documents."

Context:
{context}

Question:
{query}

Answer:"""

        try:
            return self._raw_llm_call(prompt)
        except Exception as e:
            self.logger.error(f"Error generating answer: {e}")
            return "Error generating answer from LLM."
