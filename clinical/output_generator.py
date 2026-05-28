import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class StructuredOutputGenerator:
    def __init__(self):
        pass

    def generate(self, entities: Dict[str, Any], safety_decisions: Dict[str, Any], aggregated_evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate final structured response.
        Output format:
        {
          "suspected_drug": "",
          "adverse_events": [],
          "dosage": "",
          "route": "",
          "population": "",
          "age": null,
          "weight": null,
          "hospitalization": false,
          "seriousness": [],
          "possible_relatedness": false,
          "matched_pi_results": [
            {
              "pi_name": "",
              "confidence_score": 0.0,
              "matched_sections": []
            }
          ]
        }
        """

        suspected_drug = ""
        drugs = entities.get("drug_names", [])
        if drugs:
            suspected_drug = drugs[0]
        elif aggregated_evidence.get("drug"):
            suspected_drug = aggregated_evidence.get("drug")

        dosage_list = entities.get("dosage", [])
        dosage = dosage_list[0] if dosage_list else ""

        route_list = entities.get("route", [])
        route = route_list[0] if route_list else ""

        pop_list = entities.get("population", [])
        population = pop_list[0] if pop_list else ""

        # Prepare matched_pi_results
        matched_pi_results = []
        for group in aggregated_evidence.get("evidence_groups", []):
            pi_result = {
                "pi_name": group.get("pi_name", ""),
                "confidence_score": group.get("confidence_score", 0.0),
                "matched_sections": group.get("matched_sections", [])
            }
            # Optional: could include chunk_refs for full traceability if needed,
            # but standard output format asks for matched_sections.
            matched_pi_results.append(pi_result)

        return {
            "suspected_drug": suspected_drug,
            "adverse_events": entities.get("symptoms", []),
            "dosage": dosage,
            "route": route,
            "population": population,
            "age": entities.get("age"),
            "weight": entities.get("weight"),
            "hospitalization": safety_decisions.get("hospitalization", False),
            "seriousness": safety_decisions.get("seriousness", []),
            "possible_relatedness": safety_decisions.get("possible_relatedness", False),
            "matched_pi_results": matched_pi_results
        }
