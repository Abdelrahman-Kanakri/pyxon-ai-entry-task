"""
Retrieval Routes

RAG query and search endpoints.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
from fastapi import APIRouter, HTTPException

from ..schemas import QueryRequest, QueryResponse, ChunkResult
from src.rag_layer import Retriever, Reranker, ContextFormatter

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query documents using RAG retrieval.
    """
    try:
        logger.info(f"Processing query: {request.query}")

        # Initialize components
        retriever = Retriever()
        reranker = Reranker()

        # Build filter if document_id specified
        filter_dict = None
        if request.document_id:
            filter_dict = {"document_id": request.document_id}

        # Retrieve chunks
        chunks = retriever.retrieve(
            query=request.query,
            top_k=request.top_k * 2,  # Retrieve more for reranking
            filter_dict=filter_dict,
        )

        # Rerank
        chunks = reranker.rerank(request.query, chunks, request.top_k)

        # Enrich with filenames
        from src.knowledge_store import SQLStore
        db = SQLStore()
        
        # Cache filenames to avoid N+1 queries
        doc_filenames = {}
        
        # Serialize chunks
        chunk_results = []
        for chunk in chunks:
            doc_id = chunk["metadata"].get("document_id")
            filename = "Unknown"
            
            if doc_id:
                if doc_id not in doc_filenames:
                    try:
                        doc = db.get_document(doc_id)
                        doc_filenames[doc_id] = doc["filename"] if doc else "Unknown"
                    except:
                        doc_filenames[doc_id] = "Unknown"
                filename = doc_filenames[doc_id]
            
            # Add to metadata
            chunk["metadata"]["filename"] = filename
            
            chunk_results.append(
                ChunkResult(
                    content=chunk["content"],
                    score=chunk["score"],
                    metadata=chunk["metadata"],
                )
            )

        # Generate RAG Answer
        from src.rag_layer import ContextFormatter
        formatter = ContextFormatter()
        context = formatter.format_context(chunks)
        
        from src.parsing.llm_interpreter import LLMInterpreter
        llm = LLMInterpreter()
        answer = llm.generate_answer(request.query, context)

        logger.info(f"Generated RAG answer (Length: {len(answer)})")

        return QueryResponse(
            query=request.query,
            chunks=chunk_results,
            total_results=len(chunk_results),
            answer=answer,
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
