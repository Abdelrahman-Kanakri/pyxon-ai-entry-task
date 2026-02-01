"""
Document Parser Routes

Document upload, processing, and management endpoints.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from ..schemas import DocumentUploadResponse, DocumentInfo, DocumentListResponse
from src.ingestion import DocumentLoader
from src.parsing import DocumentClassifier
from src.chunking import FixedChunker, DynamicChunker
from src.knowledge_store import Indexer

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document.
    """
    try:
        # Save uploaded file
        upload_dir = Path("./data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Processing file: {file.filename}")

        # Extract content
        content = DocumentLoader.load_document(str(file_path))

        # Detect language with AI (superior to regex/heuristics)
        try:
            from src.parsing.llm_interpreter import LLMInterpreter
            llm = LLMInterpreter()
            # Only use AI if we have enough text
            if len(content.cleaned_text) > 20:
                detected_lang = llm.detect_language(content.cleaned_text)
                if detected_lang != "unknown":
                    content.language = detected_lang
                    logger.info(f"AI detected language: {detected_lang}")
        except Exception as e:
            logger.warning(f"AI language detection failed, keeping original: {e}")

        # Classify document
        classifier = DocumentClassifier()
        classification = classifier.classify_document(content)
        content.metadata["classification"] = classification.document_type

        # Extract structure
        from src.parsing.structural_extractor import StructuralExtractor
        struct_extractor = StructuralExtractor()
        structure = struct_extractor.extract_structure(content)
        content.structured_data["structure_outline"] = structure.outline
        
        # Extract semantics
        from src.parsing.semantic_extractor import SemanticExtractor
        sem_extractor = SemanticExtractor()
        semantics = sem_extractor.extract_semantics(content)
        content.metadata["topics"] = semantics.topics
        content.metadata["keywords"] = semantics.keywords
        content.metadata["summary"] = semantics.summary

        # Choose chunking strategy
        if classification.recommended_strategy.value == "fixed":
            chunker = FixedChunker()
        else:
            chunker = DynamicChunker()

        # Create chunks
        chunks = chunker.chunk_text(content.cleaned_text)

        # Validate chunks
        from src.chunking.chunk_validator import ChunkValidator
        validator = ChunkValidator()
        validation_report = validator.validate_chunks(chunks)
        content.metadata["chunk_validation"] = {
            "valid_ratio": f"{validation_report['valid_chunks']}/{validation_report['total_chunks']}",
            "avg_quality": round(validation_report['average_quality_score'], 2)
        }

        # Index document
        indexer = Indexer()
        document_id = indexer.index_document(content, chunks, filename=file.filename)

        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            status="completed",
            chunk_count=len(chunks),
            message=f"Document processed successfully (Lang: {content.language})",
        )

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """
    List all processed documents.
    """
    try:
        from src.knowledge_store import Indexer

        indexer = Indexer()
        documents = indexer.list_documents()

        doc_infos = [DocumentInfo(**doc) for doc in documents]

        return DocumentListResponse(documents=doc_infos, total=len(doc_infos))

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document.
    """
    try:
        from src.knowledge_store import Indexer

        indexer = Indexer()
        indexer.delete_document(document_id)

        return {"message": "Document deleted successfully", "document_id": document_id}

    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
