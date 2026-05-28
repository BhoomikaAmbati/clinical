import logging
import json
from pathlib import Path
from config import BASE_DIR
from retrieval.index_manager import IndexManager

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_dummy_chunks():
    """Create dummy chunks if chunked directory is empty, to test the retrievers."""
    chunks_dir = BASE_DIR / "chunked"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    file_path = chunks_dir / "dummy_chunks.json"
    if not list(chunks_dir.glob("*.json")):
        logger.info(f"Creating dummy chunks file: {file_path}")
        dummy_data = [
            {
                "chunk_id": "dummy_1",
                "drug": "dummy",
                "source_file": "dummy.json",
                "section": "root > indications",
                "text": "The patient was prescribed Actemra for rheumatoid arthritis.",
                "metadata": {}
            },
            {
                "chunk_id": "dummy_2",
                "drug": "dummy",
                "source_file": "dummy.json",
                "section": "root > warnings",
                "text": "Lucentis is injected into the eye to treat macular degeneration.",
                "metadata": {}
            },
            {
                "chunk_id": "dummy_3",
                "drug": "dummy",
                "source_file": "dummy.json",
                "section": "root > dosage",
                "text": "The recommended dose of Ocrevus is 600 mg every 6 months.",
                "metadata": {}
            },
            {
                "chunk_id": "dummy_4",
                "drug": "dummy",
                "source_file": "dummy.json",
                "section": "root > description",
                "text": "Rheumatoid arthritis is a chronic inflammatory disorder.",
                "metadata": {}
            }
        ]
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(dummy_data, f, indent=4)

def main():
    print("=== Starting Retrieval Infrastructure Test ===\n")

    # Create dummy chunks if none exist
    create_dummy_chunks()

    manager = IndexManager()

    # Build indexes
    manager.build_all()

    # Load indexes
    # Create a fresh manager to test loading works
    fresh_manager = IndexManager()
    fresh_manager.load_all()

    # Sample Query
    query = "rheumatoid arthritis treatment"
    top_k = 2

    print(f"\nRunning Query: '{query}' (top_k={top_k})")
    print("-" * 50)

    results = fresh_manager.retrieve_all(query, top_k=top_k)

    print("\n--- BM25 Results ---")
    if not results["bm25"]:
        print("No BM25 results.")
    for res in results["bm25"]:
        print(f"Chunk ID: {res['chunk_id']}")
        print(f"Score: {res['score']:.4f}")
        print(f"Text snippet: {res['chunk'].get('text', '')[:100]}...")
        print("")

    print("--- Semantic Results ---")
    if not results["semantic"]:
        print("No Semantic results.")
    for res in results["semantic"]:
        print(f"Chunk ID: {res['chunk_id']}")
        print(f"Score: {res['score']:.4f}")
        print(f"Text snippet: {res['chunk'].get('text', '')[:100]}...")
        print("")

    print("=== Retrieval Test Completed Successfully ===")

if __name__ == "__main__":
    main()
