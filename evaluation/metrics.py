import math
from typing import List, Dict, Any, Set

def precision_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    if not retrieved_ids or k <= 0:
        return 0.0
    k = min(k, len(retrieved_ids))
    retrieved_k = retrieved_ids[:k]
    relevant_retrieved = sum(1 for chunk_id in retrieved_k if chunk_id in relevant_ids)
    return relevant_retrieved / k

def recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    if not relevant_ids or k <= 0:
        return 0.0
    k = min(k, len(retrieved_ids))
    retrieved_k = retrieved_ids[:k]
    relevant_retrieved = sum(1 for chunk_id in retrieved_k if chunk_id in relevant_ids)
    return relevant_retrieved / len(relevant_ids)

def mrr(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    for i, chunk_id in enumerate(retrieved_ids):
        if chunk_id in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0

def ndcg(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    if not retrieved_ids or not relevant_ids or k <= 0:
        return 0.0
    k = min(k, len(retrieved_ids))

    dcg = 0.0
    for i in range(k):
        if retrieved_ids[i] in relevant_ids:
            # Assuming binary relevance for NDCG calculation here (1 if relevant, 0 otherwise)
            dcg += 1.0 / math.log2(i + 2)

    # Calculate IDCG (Ideal DCG)
    idcg = 0.0
    ideal_k = min(k, len(relevant_ids))
    for i in range(ideal_k):
        idcg += 1.0 / math.log2(i + 2)

    return dcg / idcg if idcg > 0 else 0.0

def calculate_metrics(ranked_chunks: List[Dict[str, Any]], ground_truth: Set[str], latency: float, failure_count: int = 0) -> Dict[str, Any]:
    retrieved_ids = [chunk.get("chunk_id") for chunk in ranked_chunks if chunk.get("chunk_id")]

    return {
        "precision@5": precision_at_k(retrieved_ids, ground_truth, 5),
        "recall@5": recall_at_k(retrieved_ids, ground_truth, 5),
        "mrr": mrr(retrieved_ids, ground_truth),
        "ndcg@5": ndcg(retrieved_ids, ground_truth, 5),
        "latency_ms": round(latency * 1000, 2),
        "failure_count": failure_count,
        "total_chunks_retrieved": len(retrieved_ids)
    }
