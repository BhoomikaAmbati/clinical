import json
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi

from core_config import BASE_DIR

logger = logging.getLogger(__name__)

class BM25Retriever:
    def __init__(self, index_dir: Path = BASE_DIR / "indexes" / "bm25"):
        self.index_dir = index_dir
        self.index_path = self.index_dir / "bm25_model.pkl"
        self.chunks_path = self.index_dir / "bm25_chunks.pkl"

        self.bm25_model = None
        self.chunks = []

        # Ensure index directory exists
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer for BM25."""
        if not text:
            return []
        return text.lower().split()

    def load_chunked_files(self, file_paths: List[Path]):
        """Load chunks from a list of JSON files."""
        self.chunks = []
        for file_path in file_paths:
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue

            try:
                with file_path.open("r", encoding="utf-8") as f:
                    file_chunks = json.load(f)
                    self.chunks.extend(file_chunks)
                logger.info(f"Loaded {len(file_chunks)} chunks from {file_path.name}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

    def build_index(self, file_paths: List[Path]):
        """Build BM25 index from a list of chunked JSON files."""
        logger.info("Building BM25 index...")
        self.load_chunked_files(file_paths)

        if not self.chunks:
            logger.warning("No chunks loaded. BM25 index will be empty.")
            self.bm25_model = None
            return

        tokenized_corpus = [self._tokenize(chunk.get("text", "")) for chunk in self.chunks]
        self.bm25_model = BM25Okapi(tokenized_corpus)
        logger.info(f"BM25 index built with {len(self.chunks)} chunks.")

    def save_index(self):
        """Persist the BM25 model and chunk mappings locally."""
        if not self.bm25_model or not self.chunks:
            logger.warning("No index to save.")
            return

        logger.info(f"Saving BM25 index to {self.index_dir}...")

        try:
            with self.index_path.open("wb") as f:
                pickle.dump(self.bm25_model, f)
            with self.chunks_path.open("wb") as f:
                pickle.dump(self.chunks, f)
            logger.info("BM25 index saved successfully.")
        except Exception as e:
            logger.error(f"Error saving BM25 index: {e}")

    def load_index(self):
        """Load the persisted BM25 model and chunk mappings."""
        if not self.index_path.exists() or not self.chunks_path.exists():
            logger.warning("BM25 index files not found.")
            return False

        logger.info(f"Loading BM25 index from {self.index_dir}...")
        try:
            with self.index_path.open("rb") as f:
                self.bm25_model = pickle.load(f)
            with self.chunks_path.open("rb") as f:
                self.chunks = pickle.load(f)
            logger.info(f"BM25 index loaded successfully with {len(self.chunks)} chunks.")
            return True
        except Exception as e:
            logger.error(f"Error loading BM25 index: {e}")
            return False

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve Top-K chunks using BM25 scoring."""
        if not self.bm25_model or not self.chunks:
            logger.warning("BM25 index is not loaded or is empty.")
            return []

        tokenized_query = self._tokenize(query)
        scores = self.bm25_model.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        for idx in top_indices:
            score = scores[idx]
            if score <= 0:
                continue # Filter out zero scores if desirable, but we'll include all top-k

            chunk = self.chunks[idx]
            results.append({
                "chunk_id": chunk.get("chunk_id", ""),
                "score": float(score),
                "retrieval_type": "bm25",
                "chunk": chunk
            })

        return results
