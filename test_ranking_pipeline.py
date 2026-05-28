import json
import logging
import pytest
from pathlib import Path

from pipeline.ranking_pipeline import RankingPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ranking_pipeline():
    # 1. Provide a mock clinical note
    clinical_note = "The patient was prescribed Actemra for rheumatoid arthritis. They have a history of severe dizziness and are taking a dosage of 600 mg intravenously."

    pipeline = RankingPipeline()

    # 2. Run the pipeline
    result = pipeline.process(clinical_note)

    # 3. Print verification info as requested
    print("\n" + "="*50)
    print("Clinical Note:")
    print(result.get("clinical_note"))

    print("\nExtracted Entities:")
    print(json.dumps(result.get("entities"), indent=2))

    print("\nGenerated Queries:")
    print(json.dumps(result.get("queries"), indent=2))

    ranked_chunks = result.get("ranked_chunks", [])
    print(f"\nTop Ranked Chunks ({len(ranked_chunks)} found):")

    for i, chunk in enumerate(ranked_chunks[:5]):
        print(f"\nRank {i+1}:")
        print(f"Chunk ID: {chunk.get('chunk_id', 'N/A')}")
        print(f"Text Snippet: {chunk.get('text', '')[:100]}...")

        fusion_score = chunk.get("score", chunk.get("rrf_score", 0.0))
        metadata_score = chunk.get("metadata_score", 0.0)
        reranker_score = chunk.get("reranker_score", 0.0)
        confidence_score = chunk.get("confidence_score", 0.0)

        print(f"Scores -> Fusion: {fusion_score:.4f} | Metadata: {metadata_score:.4f} | Reranker: {reranker_score:.4f} | Confidence: {confidence_score:.4f}")
        print(f"Matched Features: {chunk.get('matched_features', {})}")

    print("="*50 + "\n")

    assert "ranked_chunks" in result
    assert "entities" in result
    assert "queries" in result

if __name__ == "__main__":
    test_ranking_pipeline()
