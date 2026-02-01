Author: Abdelrahman Kanakri
Date: 2026-02-01
Version: 1.1.0
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Dict

# Add project root to path
sys.path.append(str(Path(__file__).parents[1]))

from src.ingestion.loader import DocumentLoader
from src.chunking.fixed_chunker import FixedChunker
from src.knowledge_store.indexer import Indexer
from src.rag_layer.retriever import Retriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_QUERIES = [
    {
        "query": "Who is the CEO of Pyxon AI?",
        "expected_terms": ["Sarah Connor", "Cyberdyne"],
    },
    {
        "query": "What formats does PyxonParser support?",
        "expected_terms": ["PDF", "DOCX", "Images"],
    },
    {
        "query": "Where is the headquarters located?",
        "expected_terms": ["Amman", "Jordan"],
    },
    {
        "query": "What is Semantic Density?",
        "expected_terms": ["complete information units", "metric"],
    },
    {
        "query": "أين يقع المقر الرئيسي لشركة بيكسون؟",
        "expected_terms": ["عمان", "الأردن"],
    },
]


async def run_benchmark():
    logger.info("Starting Benchmark Suite...")

    # 1. Setup
    sample_path = Path(__file__).parent / "sample_documents" / "benchmark_sample.txt"
    if not sample_path.exists():
        logger.error(f"Sample file not found: {sample_path}")
        return

    # 2. Ingestion & Indexing
    logger.info("Indexing sample document...")
    loader = DocumentLoader()
    content = loader.load_document(sample_path)

    chunker = FixedChunker()
    chunks = chunker.chunk_text(content.cleaned_text)

    indexer = Indexer()
    doc_id = indexer.index_document(content, chunks, filename=sample_path.name)
    logger.info(f"Indexed document {doc_id} with {len(chunks)} chunks")

    # 3. Retrieval Testing
    retriever = Retriever()
    passed = 0
    total = len(TEST_QUERIES)

    print("\n--- Benchmark Results ---\n")

    for i, test in enumerate(TEST_QUERIES):
        query = test["query"]
        expected = test["expected_terms"]

        # Retrieve
        results = retriever.retrieve(query, top_k=3)

        # Check recall
        detected = False
        retrieved_text = " ".join([r.content for r in results])

        hits = [term for term in expected if term.lower() in retrieved_text.lower()]
        if len(hits) == len(expected):
            detected = True
            passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        print(f"Query {i+1}: {query}")
        print(f"Status: {status}")
        print(f"Expected: {expected}")
        print(f"Matches: {hits}\n")

    # 4. Cleanup
    indexer.delete_document(doc_id)

    accuracy = (passed / total) * 100
    print(f"Final Accuracy: {accuracy:.1f}% ({passed}/{total})")

    if accuracy == 100:
        logger.info("Benchmark PASSED")
    else:
        logger.error("Benchmark FAILED")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
