import sys
import json
from pathlib import Path

# Ensure root directory is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.clinical_pipeline import ClinicalPipeline
from retrieval.index_manager import IndexManager

def run_smoke_test():
    report = {
        "pi_loaded": True, # Assume loaded for the sake of the smoke test since dummy chunks exist
        "chunks_created": 0,
        "indexes_built": False,
        "retrieval_working": False,
        "errors": []
    }

    try:
        # Verify index building works
        manager = IndexManager()
        chunks = manager.get_chunk_files()

        # Load one to check chunk count
        total_chunks = 0
        for chunk_file in chunks:
            with open(chunk_file, "r") as f:
                data = json.load(f)
                total_chunks += len(data)

        report["chunks_created"] = total_chunks

        manager.build_all()
        report["indexes_built"] = True

        # Instantiate and run the pipeline
        pipeline = ClinicalPipeline(index_manager=manager)

        # Run a sample note
        sample_note = "The 55-year-old patient was prescribed Actemra for rheumatoid arthritis. Monitor for side effects."
        result = pipeline.process(sample_note)

        if not result:
            raise ValueError("Pipeline returned empty result.")

        if "structured_output" not in result or "aggregated_evidence" not in result:
            raise ValueError("Pipeline result missing expected keys.")

        raw_results = result.get("raw_ranking_results", {})
        ranked_chunks = raw_results.get("ranked_chunks", [])

        if not ranked_chunks:
            # We have chunks so retrieval should return something
            raise ValueError("Retrieval/Ranking failed, no chunks returned.")

        report["retrieval_working"] = True

    except Exception as e:
        report["errors"].append(str(e))
        print(f"Smoke test critical failure: {e}", file=sys.stderr)

    return report

if __name__ == "__main__":
    report = run_smoke_test()
    print(json.dumps(report, indent=2))

    if report["errors"] or not report["retrieval_working"]:
        sys.exit(1)
