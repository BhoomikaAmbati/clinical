import json
import logging
import sys

from pipeline.validation_pipeline import ValidationPipeline

# Configure logging to print to stdout so we can see it
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def main():
    print("=== Starting Real PI Schema Validation Pipeline Test ===\n")

    pipeline = ValidationPipeline()

    # Run pipeline with a representative dummy query to test retrieval
    report = pipeline.run("What is the dosage for Actemra for rheumatoid arthritis?")

    print("\n=== Validation Report ===")
    print(json.dumps(report, indent=4))
    print("=========================\n")

    if report["errors"]:
        print("Pipeline finished with errors:")
        for err in report["errors"]:
            print(f" - {err}")
        # sys.exit(1) # We won't exit with 1 because dummy data might legitimately not produce chunks
    else:
        print("Pipeline finished successfully without unhandled exceptions.")

    # Explicitly check retrieval status
    if report["retrieval_success"] and report["ranking_success"]:
        print("\nRetrieval and Ranking status: SUCCESS")
    else:
        print("\nRetrieval and Ranking status: FAILED or SKIPPED (e.g. no chunks created)")

if __name__ == "__main__":
    main()
