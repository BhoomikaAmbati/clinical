import json
import logging
import pickle
import numpy as np
import faiss
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

from core_config import BASE_DIR

logger = logging.getLogger(__name__)

class SemanticRetriever:
    def __init__(self, index_dir: Path = BASE_DIR / "indexes" / "faiss", model_name: str = "all-MiniLM-L6-v2"):
        self.index_dir = index_dir
        self.index_path = self.index_dir / "faiss_index.bin"
        self.chunks_path = self.index_dir / "faiss_chunks.pkl"
        self.model_name = model_name

        self.model = SentenceTransformer(self.model_name)
        self.index = None
        self.chunks = []

        # Ensure index directory exists
        self.index_dir.mkdir(parents=True, exist_ok=True)

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
        """Build FAISS semantic index from a list of chunked JSON files."""
        logger.info("Building Semantic index...")
        self.load_chunked_files(file_paths)

        if not self.chunks:
            logger.warning("No chunks loaded. Semantic index will be empty.")
            self.index = None
            return

        texts = [chunk.get("text", "") for chunk in self.chunks]

        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=False)

        # Convert to numpy array
        embeddings = np.array(embeddings).astype("float32")

        # Initialize FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

        logger.info(f"Semantic index built with {self.index.ntotal} vectors of dimension {dimension}.")

    def save_index(self):
        """Persist the FAISS index and chunk mappings locally."""
        if self.index is None or not self.chunks:
            logger.warning("No semantic index to save.")
            return

        logger.info(f"Saving Semantic index to {self.index_dir}...")

        try:
            faiss.write_index(self.index, str(self.index_path))
            with self.chunks_path.open("wb") as f:
                pickle.dump(self.chunks, f)
            logger.info("Semantic index saved successfully.")
        except Exception as e:
            logger.error(f"Error saving Semantic index: {e}")

    def load_index(self):
        """Load the persisted FAISS index and chunk mappings."""
        if not self.index_path.exists() or not self.chunks_path.exists():
            logger.warning("Semantic index files not found.")
            return False

        logger.info(f"Loading Semantic index from {self.index_dir}...")
        try:
            self.index = faiss.read_index(str(self.index_path))
            with self.chunks_path.open("rb") as f:
                self.chunks = pickle.load(f)
            logger.info(f"Semantic index loaded successfully with {self.index.ntotal} vectors.")
            return True
        except Exception as e:
            logger.error(f"Error loading Semantic index: {e}")
            return False

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve Top-K chunks using semantic vector search."""
        if self.index is None or not self.chunks:
            logger.warning("Semantic index is not loaded or is empty.")
            return []

        # Generate embedding for the query
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        # Perform vector search
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1: # FAISS returns -1 if there are fewer than k results
                continue

            distance = float(distances[0][i])
            # For L2 distance, lower is better. We can invert it to represent a score where higher is better,
            # or just return it as a score. We'll return inverted distance as score for consistency (higher=better),
            # but standardizing the "score" value might be fine.
            # We'll use 1 / (1 + distance)
            score = 1.0 / (1.0 + distance)

            chunk = self.chunks[idx]
            results.append({
                "chunk_id": chunk.get("chunk_id", ""),
                "score": score,
                "retrieval_type": "semantic",
                "chunk": chunk
            })

        return results
