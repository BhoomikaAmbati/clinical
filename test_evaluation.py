import json
import logging
from deployment.local_setup import validate_setup
from deployment.smoke_test import run_smoke_test
from evaluation.regression_tests import run_all as run_regression_tests
from evaluation.benchmark import run_benchmark
from pipeline.clinical_pipeline import ClinicalPipeline
from retrieval.index_manager import IndexManager

# Suppress debug logs
logging.getLogger().setLevel(logging.ERROR)

def main():
    print("="*50)
    print("PHASE 10: VALIDATION, EVALUATION, AND HARDENING")
    print("="*50)

    # 1. Local Setup Validation
    print("\n[1/4] Running Local Setup Validation...")
    setup_report = validate_setup()
    print(json.dumps(setup_report, indent=2))
    if setup_report["status"] != "success":
        print(">> FAILED: Local setup validation.")
        return

    # 2. Smoke Testing
    print("\n[2/4] Running Smoke Tests...")
    smoke_report = run_smoke_test()
    print(json.dumps(smoke_report, indent=2))
    if smoke_report["errors"] or not smoke_report["retrieval_working"]:
        print(">> FAILED: Smoke testing.")
        return

    # 3. Regression Testing
    print("\n[3/4] Running Regression Tests...")
    regression_report = run_regression_tests()
    print(json.dumps(regression_report, indent=2))
    if regression_report["failed"] > 0:
        print(">> FAILED: Regression tests.")
        return

    # 4. Benchmarking
    print("\n[4/4] Running Benchmarking...")
    manager = IndexManager()
    manager.build_all()
    pipeline = ClinicalPipeline(index_manager=manager)
    benchmark_note = "The 55-year-old patient was prescribed Actemra for rheumatoid arthritis. Monitor for side effects."
    benchmark_report = run_benchmark(pipeline, benchmark_note)
    print(json.dumps(benchmark_report, indent=2))

    print("\n" + "="*50)
    print("ALL TESTS PASSED SUCCESSFULLY.")
    print("="*50)

if __name__ == "__main__":
    main()
