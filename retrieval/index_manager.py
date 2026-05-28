import logging
from pathlib import Path
from typing import List, Dict, Any

from config import BASE_DIR
from retrieval.bm25 import BM25Retriever
from retrieval.semantic import SemanticRetriever

logger = logging.getLogger(__name__)

class IndexManager:
    def __init__(self, chunks_dir: Path = BASE_DIR / "chunked"):
        self.chunks_dir = chunks_dir

        self.bm25 = BM25Retriever()
        self.semantic = SemanticRetriever()

    def get_chunk_files(self) -> List[Path]:
        """Returns all JSON files in the chunks directory."""
        if not self.chunks_dir.exists():
            logger.warning(f"Chunks directory not found: {self.chunks_dir}")
            return []
        return list(self.chunks_dir.glob("*.json"))

    def build_all(self):
        """Build and save all indexes."""
        chunk_files = self.get_chunk_files()
        if not chunk_files:
            logger.warning("No chunk files found to build indexes from.")
            return

        logger.info("Building all indexes...")

        # Build BM25
        self.bm25.build_index(chunk_files)
        self.bm25.save_index()

        # Build Semantic
        self.semantic.build_index(chunk_files)
        self.semantic.save_index()

        logger.info("All indexes built and saved.")

    def load_all(self):
        """Load all indexes."""
        logger.info("Loading all indexes...")

        bm25_loaded = self.bm25.load_index()
        semantic_loaded = self.semantic.load_index()

        if bm25_loaded and semantic_loaded:
            logger.info("All indexes loaded successfully.")
        else:
            logger.warning(f"Indexes partially loaded: BM25({bm25_loaded}), Semantic({semantic_loaded})")

    def retrieve_all(self, query: str, top_k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Query all retrievers and return their combined results."""
        return {
            "bm25": self.bm25.search(query, top_k=top_k),
            "semantic": self.semantic.search(query, top_k=top_k)
        }
