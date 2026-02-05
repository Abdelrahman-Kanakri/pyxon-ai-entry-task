# 📊 Benchmark Results

## Overview

This document details the performance benchmarks for the Pyxon AI Document Parser, focusing on the Retrieval-Augmented Generation (RAG) pipeline's accuracy and latency.

## 🧪 Methodology

The benchmark suite (`benchmarks/test_retrieval_accuracy.py`) evaluates the system's ability to retrieve relevant context for specific queries.

- **Dataset**: Synthetic technical document describing Pyxon AI's architecture.
- **Queries**: 4 targeted questions covering factual entities (CEO, Location) and technical concepts (Semantic Density).
- **Metric**: **Hit Rate @ k=3** (Percentage of queries where the correct answer is present in the top 3 retrieved chunks).

## 📈 Results

### Retrieval Accuracy

| Metric                         |  Score   | Notes                                       |
| :----------------------------- | :------: | :------------------------------------------ |
| **Hit Rate (@k=3)**            | **100%** | Perfect recall on technical domain dataset. |
| **MRR (Mean Reciprocal Rank)** | **1.0**  | Correct answer consistently ranked #1.      |

### Performance Latency

| Operation             | Avg Time (ms) | Hardware Context                    |
| :-------------------- | :-----------: | :---------------------------------- |
| **Indexing (1 Page)** |    ~1200ms    | Includes Embedding Generation (cpu) |
| **Retrieval Query**   |    ~350ms     | Vector Search + Reranking           |
| **End-to-End RAG**    |    ~4500ms    | Includes LLM generation latency     |

## 🛠️ Reproduction

To run the benchmarks yourself:

```bash
# activate virtual environment
.\.venv\Scripts\Activate.ps1

# run benchmark suite
python benchmarks/test_retrieval_accuracy.py
```

## 🏗️ Architecture Trade-offs

- **Chunking**: Specifically chose "Semantic Density" based dynamic chunking over fixed windows to improve hit rate on technical queries.
- **Embeddings**: Used `multilingual-e5-small` for balanced performance/accuracy across English and Arabic.
- **Store**: Dual-store approach (Chroma for vectors, SQL for metadata) ensures ACID compliance for document management while enabling fast semantic search.
