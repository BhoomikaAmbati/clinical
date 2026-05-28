import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class PIAggregator:
    def __init__(self):
        pass

    def aggregate(self, fused_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregates chunk scores belonging to the same PI source.

        :param fused_results: A list of fused document dictionaries, output of RRFusion.fuse()
        :return: A list of aggregated dictionaries, sorted by aggregated_score descending.
        """
        pi_map = {}

        for item in fused_results:
            chunk = item.get("chunk", {})
            # Try to get drug name or source file as PI identifier
            pi_name = chunk.get("drug") or chunk.get("source_file") or "unknown_pi"

            if pi_name not in pi_map:
                pi_map[pi_name] = {
                    "pi_name": pi_name,
                    "aggregated_score": 0.0,
                    "chunks": []
                }

            pi_map[pi_name]["aggregated_score"] += item["rrf_score"]
            pi_map[pi_name]["chunks"].append(item)

        # Convert map to list and sort by aggregated score descending
        aggregated_results = list(pi_map.values())
        aggregated_results.sort(key=lambda x: x["aggregated_score"], reverse=True)

        return aggregated_results
