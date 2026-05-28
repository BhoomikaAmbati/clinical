import os
from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Known PI filenames
PI_FILENAMES = [
    "actemra_v53_2025.json",
    "lucentis_v27_2025 5.json",
    "ocrevus_v22_2025.json"
]

# Retrieval Configuration
TOP_K = 5
BM25_INDEX_DIR = BASE_DIR / "indexes" / "bm25"
FAISS_INDEX_DIR = BASE_DIR / "indexes" / "faiss"
CHUNKS_DIR = BASE_DIR / "chunked"
SEMANTIC_MODEL_NAME = "all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Fusion Configuration
RRF_K = 60
SIMILARITY_THRESHOLD = 0.9

# Scoring Configuration
METADATA_WEIGHTS = {
    "drug": 2.0,
    "symptom": 1.5,
    "dosage": 1.0,
    "frequency": 1.0,
    "route": 1.0,
    "population": 1.0,
    "icd": 1.5,
    "j_code": 1.5,
    "black_box": 2.0,
    "temporal": 1.0
}

CONFIDENCE_WEIGHTS = {
    "fusion": 1.0,
    "metadata": 1.0,
    "reranker": 1.0
}