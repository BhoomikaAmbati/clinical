from typing import Dict, Any, List

class SchemaAdapter:
    def __init__(self, mapping_config: Dict[str, str] = None):
        """
        mapping_config maps internal standardized keys to possible external schema keys.
        e.g. {"dosage": "dosage_and_administration", "warnings": "boxed_warning"}
        """
        # Default fallbacks or configurable overrides
        self.mapping_config = mapping_config or {}

    def adapt(self, drug_name: str, raw_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts unknown PI schemas into standardized internal schema.
        Standardized output:
        {
            "drug": ...,
            "section": ..., # Can be hierarchical or root
            "text": ...,
            "metadata": {
                "dosage": ...,
                "route": ...,
                "population": ...,
                "warnings": ...,
                "j_codes": ...,
                "black_box": ...
            }
        }
        """
        # A simple flattened version preserving standard keys.
        # Since chunker traverses anyway, the adapter could reorganize the JSON
        # so it follows a predictable structure or explicitly extracts metadata.

        adapted = {
            "drug": drug_name,
            "content": {},
            "metadata": {
                "dosage": None,
                "route": None,
                "population": None,
                "warnings": None,
                "j_codes": None,
                "black_box": None
            }
        }

        # Fallback mapping list to look for keys heuristically
        metadata_hints = {
            "dosage": ["dosage", "dose", "dosage_and_administration"],
            "route": ["route", "administration", "route_of_administration"],
            "population": ["population", "pediatric", "geriatric", "specific_populations"],
            "warnings": ["warnings", "precautions", "warnings_and_precautions"],
            "j_codes": ["j_code", "hcpcs", "billing_code"],
            "black_box": ["black_box", "boxed_warning", "warning_box"]
        }

        # Override with config if provided
        for std_key, external_key in self.mapping_config.items():
            if std_key in metadata_hints:
                # Add to the front so it checks config first
                metadata_hints[std_key].insert(0, external_key)

        def _extract(current_data, current_path):
            if isinstance(current_data, dict):
                for k, v in current_data.items():
                    # Check if key matches a metadata hint
                    k_lower = str(k).lower()
                    matched_meta = False
                    for std_key, hints in metadata_hints.items():
                        if any(hint in k_lower for hint in hints):
                            # Try to extract the first string value for metadata if it's nested
                            # Or just assign if string
                            if isinstance(v, str):
                                if adapted["metadata"][std_key] is None:
                                    adapted["metadata"][std_key] = v
                                matched_meta = True
                                break
                            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], str):
                                if adapted["metadata"][std_key] is None:
                                    adapted["metadata"][std_key] = v[0]
                                matched_meta = True
                                break

                    # Always include in content to preserve raw values and text
                    if current_path:
                        path_key = " > ".join(current_path + [str(k)])
                    else:
                        path_key = str(k)

                    adapted["content"][path_key] = v
                    _extract(v, current_path + [str(k)])

            elif isinstance(current_data, list):
                for i, item in enumerate(current_data):
                    _extract(item, current_path)

        _extract(raw_schema, [])

        # In case it's not a dict, just put it in content
        if not isinstance(raw_schema, dict):
             adapted["content"]["root"] = raw_schema

        return adapted
