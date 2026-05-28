import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.clinical_pipeline import ClinicalPipeline
from retrieval.index_manager import IndexManager

def run_all() -> Dict[str, Any]:
    manager = IndexManager()
    manager.build_all()
    pipeline = ClinicalPipeline(index_manager=manager)

    report = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "failures": []
    }

    def assert_test(name, condition, error_msg):
        report["total_tests"] += 1
        if condition:
            report["passed"] += 1
        else:
            report["failed"] += 1
            report["failures"].append({name: error_msg})

    # Test 1: Empty note
    try:
        res = pipeline.process("")
        assert_test("empty_note", isinstance(res, dict) and "structured_output" in res, "Failed to gracefully handle empty note.")
    except Exception as e:
        assert_test("empty_note", False, str(e))

    # Test 2: Large Note
    try:
        res = pipeline.process("rheumatoid arthritis " * 1000)
        assert_test("large_note", isinstance(res, dict) and "structured_output" in res, "Failed to gracefully handle large note.")
    except Exception as e:
        assert_test("large_note", False, str(e))

    # Test 3: Invalid input type
    try:
        pipeline.process(None)
        assert_test("invalid_input", False, "Should have raised TypeError or handled gracefully.")
    except Exception as e:
        # If it raises an exception, we consider it handled correctly in this regression test
        assert_test("invalid_input", True, "")

    return report

if __name__ == "__main__":
    import json
    print(json.dumps(run_all(), indent=2))
