import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class RRFusion:
    def __init__(self, k: int = 60):
        self.k = k

    def fuse(self, results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Fuses retrieval outputs from multiple sources using Reciprocal Rank Fusion.

        :param results: A dictionary where keys are retrieval method names (e.g., "bm25", "semantic")
                        and values are lists of ranked document dictionaries.
                        Each document dictionary must have "chunk_id" and "chunk".
        :return: A list of fused document dictionaries, sorted by rrf_score in descending order.
        """
        fused_scores = {}
        sources_map = {}
        chunks_map = {}

        for method, doc_list in results.items():
            # Process each list of documents, assuming they are pre-sorted by rank
            for rank, doc in enumerate(doc_list):
                chunk_id = doc["chunk_id"]
                chunk_data = doc.get("chunk", {})

                # Formula: 1 / (k + rank), assuming 1-based rank (so rank + 1)
                score_contrib = 1.0 / (self.k + rank + 1)

                if chunk_id not in fused_scores:
                    fused_scores[chunk_id] = 0.0
                    sources_map[chunk_id] = []
                    chunks_map[chunk_id] = chunk_data

                fused_scores[chunk_id] += score_contrib
                if method not in sources_map[chunk_id]:
                    sources_map[chunk_id].append(method)

        # Build final output
        fused_results = []
        for chunk_id, score in fused_scores.items():
            fused_results.append({
                "chunk_id": chunk_id,
                "rrf_score": score,
                "retrieval_sources": sources_map[chunk_id],
                "chunk": chunks_map[chunk_id]
            })

        # Sort by RRF score descending
        fused_results.sort(key=lambda x: x["rrf_score"], reverse=True)

        return fused_results
