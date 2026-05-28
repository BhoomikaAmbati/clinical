import logging
from retrieval.index_manager import IndexManager
from retrieval.fusion_pipeline import FusionPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("=== Starting Fusion Pipeline Test ===\n")

    manager = IndexManager()
    manager.load_all()

    # Query used in test_retrieval.py or use dummy query
    query = "rheumatoid arthritis treatment"
    top_k = 5

    print(f"\nRunning Query: '{query}' (top_k={top_k})")
    print("-" * 50)

    retrieval_results = manager.retrieve_all(query, top_k=top_k)

    print("\n--- Retrieval Counts ---")
    for method, results in retrieval_results.items():
        print(f"{method}: {len(results)} results")

    pipeline = FusionPipeline()
    pipeline_results = pipeline.run(retrieval_results)

    print("\n--- RRF Results (Top 3) ---")
    fused_results = pipeline_results["fused_results"]
    for i, res in enumerate(fused_results[:3]):
        print(f"Rank {i+1}: Chunk {res['chunk_id']} | RRF Score: {res['rrf_score']:.4f} | Sources: {res['retrieval_sources']}")

    print(f"\n--- Duplicate Reduction Stats ---")
    print(f"Total fused chunks: {len(fused_results)}")
    print(f"Duplicates removed: {pipeline_results['duplicates_removed']}")
    print(f"Remaining chunks: {len(pipeline_results['deduplicated_results'])}")

    print("\n--- Final Ranked PI List ---")
    for i, pi in enumerate(pipeline_results["final_ranked_pis"]):
        print(f"Rank {i+1}: PI '{pi['pi_name']}' | Aggregated Score: {pi['aggregated_score']:.4f} | Contributing Chunks: {len(pi['chunks'])}")

    print("\n=== Fusion Pipeline Test Completed Successfully ===")

if __name__ == "__main__":
    main()
