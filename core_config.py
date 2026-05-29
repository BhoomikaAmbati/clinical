import os
from pathlib import Path

# Re-export from settings to maintain backward compatibility
from config.settings import (
    BASE_DIR,
    DATA_DIR,
    PI_FILENAMES,
    TOP_K,
    BM25_INDEX_DIR,
    FAISS_INDEX_DIR,
    CHUNKS_DIR,
    SEMANTIC_MODEL_NAME,
    RERANKER_MODEL_NAME,
    RRF_K,
    SIMILARITY_THRESHOLD,
    METADATA_WEIGHTS,
    CONFIDENCE_WEIGHTS
)
