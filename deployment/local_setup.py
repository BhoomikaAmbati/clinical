import os
import sys
import importlib
from pathlib import Path
from typing import Dict, Any, List

# Ensure root directory is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def validate_setup() -> Dict[str, Any]:
    from core_config import BASE_DIR, DATA_DIR, CHUNKS_DIR, BM25_INDEX_DIR, FAISS_INDEX_DIR

    report = {
        "status": "success",
        "missing_folders": [],
        "missing_files": [],
        "missing_dependencies": [],
        "missing_indexes": [],
        "details": {}
    }

    # Required folders
    required_folders = [
        DATA_DIR,
        CHUNKS_DIR,
        BM25_INDEX_DIR,
        FAISS_INDEX_DIR,
        BASE_DIR / "indexes"
    ]
    for folder in required_folders:
        if not folder.exists():
            report["missing_folders"].append(str(folder))

    # Required files
    required_files = [
        BASE_DIR / "core_config.py",
        BASE_DIR / "config" / "settings.py"
    ]
    for file in required_files:
        if not file.exists():
            report["missing_files"].append(str(file))

    # Check dependencies
    required_deps = [
        "sentence_transformers",
        "rank_bm25",
        "faiss",
        "fastapi",
        "uvicorn",
        "pydantic"
    ]
    for dep in required_deps:
        try:
            importlib.import_module(dep)
        except ImportError:
            report["missing_dependencies"].append(dep)

    # Check Indexes
    if not (BM25_INDEX_DIR / "bm25_model.pkl").exists() or not (BM25_INDEX_DIR / "bm25_chunks.pkl").exists():
        report["missing_indexes"].append("bm25")

    if not (FAISS_INDEX_DIR / "faiss_index.bin").exists() or not (FAISS_INDEX_DIR / "faiss_chunks.pkl").exists():
        report["missing_indexes"].append("faiss")

    if any([
        report["missing_folders"],
        report["missing_files"],
        report["missing_dependencies"],
        report["missing_indexes"]
    ]):
        report["status"] = "failed"

    return report

if __name__ == "__main__":
    import json
    print(json.dumps(validate_setup(), indent=2))
