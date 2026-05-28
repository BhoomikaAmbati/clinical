import time
import tracemalloc
from typing import Dict, Any

from pipeline.clinical_pipeline import ClinicalPipeline

def run_benchmark(pipeline: ClinicalPipeline, note: str) -> Dict[str, Any]:
    report = {
        "end_to_end_latency_s": 0.0,
        "memory_peak_mb": 0.0,
        "memory_current_mb": 0.0,
        "success": False
    }

    tracemalloc.start()
    start_time = time.time()

    try:
        # Run end-to-end processing
        pipeline.process(note)
        report["success"] = True
    except Exception as e:
        print(f"Benchmark run failed: {e}")
    finally:
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        report["end_to_end_latency_s"] = round(end_time - start_time, 4)
        report["memory_current_mb"] = round(current / 10**6, 2)
        report["memory_peak_mb"] = round(peak / 10**6, 2)

    return report
