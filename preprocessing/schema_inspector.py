import json
from typing import Dict, Any, List

class SchemaInspector:
    def __init__(self):
        pass

    def inspect(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspects arbitrary JSON structures recursively and detects top-level keys,
        nested depth, common field names, arrays vs objects, text-heavy sections,
        and metadata candidates.
        """
        summary = {
            "top_level_keys": [],
            "nested_depth": 0,
            "text_fields": [],
            "metadata_candidates": [],
            "array_fields": [],
            "object_fields": [],
            "all_keys": set()
        }

        if not isinstance(data, dict):
            return summary

        summary["top_level_keys"] = list(data.keys())

        def _traverse(current_data, current_depth, current_path):
            if current_depth > summary["nested_depth"]:
                summary["nested_depth"] = current_depth

            if isinstance(current_data, dict):
                for k, v in current_data.items():
                    summary["all_keys"].add(k)

                    if isinstance(v, dict):
                        summary["object_fields"].append(k)
                        _traverse(v, current_depth + 1, current_path + [k])
                    elif isinstance(v, list):
                        summary["array_fields"].append(k)
                        _traverse(v, current_depth + 1, current_path + [k])
                    elif isinstance(v, str):
                        # Simple heuristic for text-heavy fields
                        if len(v) > 100:
                            if k not in summary["text_fields"]:
                                summary["text_fields"].append(k)
                        elif k in ["dosage", "route", "population", "warnings", "j_codes", "black_box"] or "code" in k or "id" in k:
                             if k not in summary["metadata_candidates"]:
                                summary["metadata_candidates"].append(k)
                        else:
                             # Could also be considered text but short, ignoring for strict text-heavy definition
                             pass
                    else:
                        # Primitives like int, bool, etc. are good metadata candidates
                        if k not in summary["metadata_candidates"]:
                            summary["metadata_candidates"].append(k)

            elif isinstance(current_data, list):
                for item in current_data:
                    _traverse(item, current_depth, current_path)

        _traverse(data, 1, [])

        # Clean up sets for JSON serialization if needed, though they aren't explicitly required in return format
        summary["all_keys"] = list(summary["all_keys"])
        # Deduplicate
        summary["text_fields"] = list(set(summary["text_fields"]))
        summary["metadata_candidates"] = list(set(summary["metadata_candidates"]))
        summary["array_fields"] = list(set(summary["array_fields"]))
        summary["object_fields"] = list(set(summary["object_fields"]))

        return {
             "top_level_keys": summary["top_level_keys"],
             "nested_depth": summary["nested_depth"],
             "text_fields": summary["text_fields"],
             "metadata_candidates": summary["metadata_candidates"]
        }
