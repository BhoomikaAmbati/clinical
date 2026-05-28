import logging
from typing import List, Dict, Any

try:
    from sentence_transformers import CrossEncoder
except ImportError:
    CrossEncoder = None

logger = logging.getLogger(__name__)

class ContextualReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize the CrossEncoder model for reranking.
        Defaults to a lightweight MS MARCO model suitable for ranking tasks.
        """
        self.model_name = model_name
        self.model = None

        if CrossEncoder is not None:
            try:
                self.model = CrossEncoder(self.model_name)
                logger.info(f"Loaded CrossEncoder model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load CrossEncoder model {self.model_name}: {e}")
        else:
            logger.warning("sentence-transformers is not installed. CrossEncoder reranking will be a no-op.")

    def rerank(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rerank a list of retrieved chunks based on their relevance to the query.

        :param query: The combined query text or original clinical note text to use for reranking.
        :param results: A list of result dictionaries, each containing at least 'chunk_id' and 'text'.
        :return: The results list sorted by 'reranker_score' in descending order. Each dict includes 'reranker_score'.
        """
        if not results:
            return []

        if self.model is None:
            # Fallback if model could not be loaded
            logger.warning("CrossEncoder model is not available. Returning original results with reranker_score = 1.0.")
            for res in results:
                res["reranker_score"] = 1.0
            return results

        # Prepare pairs for the CrossEncoder
        pairs = []
        for res in results:
            text = res.get("text", "")
            pairs.append((query, text))

        try:
            # Predict scores using the CrossEncoder
            scores = self.model.predict(pairs)

            # Attach scores to results
            for i, res in enumerate(results):
                res["reranker_score"] = float(scores[i])

            # Sort results by the new reranker_score in descending order
            reranked_results = sorted(results, key=lambda x: x["reranker_score"], reverse=True)
            return reranked_results

        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            for res in results:
                res["reranker_score"] = 0.0
            return results
