import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MetadataScorer:
    def __init__(self, weights: Dict[str, float] = None):
        # Configurable weights for metadata scoring signals
        self.weights = weights or {
            "drug": 2.0,
            "symptom": 1.5,
            "dosage": 1.0,
            "frequency": 1.0,
            "route": 1.0,
            "population": 1.0,
            "icd": 1.5,
            "j_code": 1.5,
            "black_box": 2.0,
            "temporal": 1.0
        }

    def score(self, entities: Dict[str, Any], chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare extracted clinical entities against chunk metadata to generate a metadata score.
        """
        metadata_score = 0.0
        matched_features = {}

        chunk_metadata = chunk.get("metadata", {})
        if not isinstance(chunk_metadata, dict):
            chunk_metadata = {}

        # Safe extraction of entity lists/values
        extracted_drugs = entities.get("drug_names", [])
        extracted_symptoms = entities.get("symptoms", [])
        extracted_dosage = entities.get("dosage", [])
        extracted_frequency = entities.get("frequency", [])
        extracted_route = entities.get("route", [])
        extracted_population = entities.get("population", [])
        extracted_icd = entities.get("icd_codes", [])
        extracted_j_code = entities.get("j_codes", [])
        extracted_temporal = entities.get("temporal", [])

        # Helper function for matching
        def _match_list(entity_list: List[str], chunk_val: Any) -> bool:
            if not entity_list or not chunk_val:
                return False
            if isinstance(chunk_val, str):
                chunk_vals = [chunk_val.lower()]
            elif isinstance(chunk_val, list):
                chunk_vals = [str(v).lower() for v in chunk_val]
            else:
                return False

            for e in entity_list:
                e_lower = str(e).lower()
                for c in chunk_vals:
                    if e_lower in c or c in e_lower:
                        return True
            return False

        def _exact_or_partial_match(entity_list: List[str], chunk_val: Any) -> float:
            if not entity_list or not chunk_val:
                return 0.0
            if isinstance(chunk_val, str):
                chunk_vals = [chunk_val.lower()]
            elif isinstance(chunk_val, list):
                chunk_vals = [str(v).lower() for v in chunk_val]
            else:
                return 0.0

            best_score = 0.0
            for e in entity_list:
                e_lower = str(e).lower()
                for c in chunk_vals:
                    if e_lower == c:
                        return 1.0
                    elif e_lower in c or c in e_lower:
                        best_score = max(best_score, 0.5)
            return best_score

        # 1. Drug match
        chunk_drug = chunk.get("drug") or chunk_metadata.get("drug", "")
        drug_match_score = _exact_or_partial_match(extracted_drugs, chunk_drug)
        if drug_match_score > 0:
            matched_features["drug"] = True
            metadata_score += self.weights["drug"] * drug_match_score

        # 2. Symptom match
        symptom_match_score = _exact_or_partial_match(extracted_symptoms, chunk_metadata.get("symptoms", []))
        if symptom_match_score > 0:
            matched_features["symptom"] = True
            metadata_score += self.weights["symptom"] * symptom_match_score

        # 3. Dosage match
        dosage_match_score = _exact_or_partial_match(extracted_dosage, chunk_metadata.get("dosage", []))
        if dosage_match_score > 0:
            matched_features["dosage"] = True
            metadata_score += self.weights["dosage"] * dosage_match_score

        # 4. Frequency match
        frequency_match_score = _exact_or_partial_match(extracted_frequency, chunk_metadata.get("frequency", []))
        if frequency_match_score > 0:
            matched_features["frequency"] = True
            metadata_score += self.weights["frequency"] * frequency_match_score

        # 5. Route match
        route_match_score = _exact_or_partial_match(extracted_route, chunk_metadata.get("route", []))
        if route_match_score > 0:
            matched_features["route"] = True
            metadata_score += self.weights["route"] * route_match_score

        # 6. Population match
        pop_match_score = _exact_or_partial_match(extracted_population, chunk_metadata.get("population", []))
        if pop_match_score > 0:
            matched_features["population"] = True
            metadata_score += self.weights["population"] * pop_match_score

        # 7. ICD match
        icd_match_score = _exact_or_partial_match(extracted_icd, chunk_metadata.get("icd_codes", []))
        if icd_match_score > 0:
            matched_features["icd"] = True
            metadata_score += self.weights["icd"] * icd_match_score

        # 8. J code match
        jcode_match_score = _exact_or_partial_match(extracted_j_code, chunk_metadata.get("j_codes", []))
        if jcode_match_score > 0:
            matched_features["j_code"] = True
            metadata_score += self.weights["j_code"] * jcode_match_score

        # 9. Black box relevance
        is_black_box = str(chunk_metadata.get("black_box", "false")).lower() == "true"
        seriousness = entities.get("seriousness", [])
        if is_black_box and _match_list(seriousness, ["severe", "life-threatening", "critical", "high"]):
            matched_features["black_box"] = True
            metadata_score += self.weights["black_box"]

        # 10. Temporal relevance
        temporal_match_score = _exact_or_partial_match(extracted_temporal, chunk_metadata.get("temporal", []))
        if temporal_match_score > 0:
            matched_features["temporal"] = True
            metadata_score += self.weights["temporal"] * temporal_match_score

        return {
            "metadata_score": round(metadata_score, 4),
            "matched_features": matched_features
        }
