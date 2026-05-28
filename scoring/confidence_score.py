import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfidenceScorer:
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize the confidence scorer with weights for the different components.
        """
        self.weights = weights or {
            "fusion": 1.0,
            "metadata": 1.0,
            "reranker": 1.0
        }

    def calculate(self, fusion_score: float, metadata_score: float, reranker_score: float) -> Dict[str, float]:
        """
        Calculate the overall confidence score.
        Final score = fusion * metadata * reranker
        """
        f_score = max(fusion_score, 0.0)
        m_score = max(metadata_score, 0.0)

        m_multiplier = max(1.0, m_score * self.weights.get("metadata", 1.0))
        f_multiplier = f_score * self.weights.get("fusion", 1.0)
        r_multiplier = max(0.01, reranker_score) * self.weights.get("reranker", 1.0)

        confidence_score = f_multiplier * m_multiplier * r_multiplier

        return {
            "confidence_score": round(float(confidence_score), 4)
        }
