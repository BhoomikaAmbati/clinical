import logging
from typing import Dict, List, Any

from retrieval.rrf import RRFusion
from retrieval.deduplication import DuplicateReducer
from retrieval.fusion import PIAggregator

logger = logging.getLogger(__name__)

class FusionPipeline:
    def __init__(self, rrf_k: int = 60, similarity_threshold: float = 0.9):
        self.rrf = RRFusion(k=rrf_k)
        self.reducer = DuplicateReducer(similarity_threshold=similarity_threshold)
        self.aggregator = PIAggregator()

    def run(self, retrieval_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Orchestrates the fusion pipeline:
        1. RRF fusion
        2. Duplicate reduction
        3. PI aggregation
        4. Final ranking

        :param retrieval_results: The output from multiple retrievers
        :return: A dictionary containing intermediate and final results
        """
        logger.info("Starting Fusion Pipeline")

        # 1. RRF Fusion
        fused_results = self.rrf.fuse(retrieval_results)
        logger.info(f"RRF Fusion complete. {len(fused_results)} unique chunks scored.")

        # 2. Duplicate Reduction
        deduplicated_results = self.reducer.reduce(fused_results)
        duplicates_removed = len(fused_results) - len(deduplicated_results)
        logger.info(f"Duplicate reduction complete. Removed {duplicates_removed} duplicates.")

        # 3. PI Aggregation
        aggregated_results = self.aggregator.aggregate(deduplicated_results)
        logger.info(f"PI Aggregation complete. Found {len(aggregated_results)} unique PIs.")

        # Final ranked PI list is aggregated_results since it's already sorted by aggregated_score

        return {
            "fused_results": fused_results,
            "deduplicated_results": deduplicated_results,
            "duplicates_removed": duplicates_removed,
            "final_ranked_pis": aggregated_results
        }
