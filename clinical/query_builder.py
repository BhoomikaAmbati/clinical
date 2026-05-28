from typing import Dict, Any, List

class ClinicalQueryBuilder:
    def __init__(self, strategies: List[str] = None):
        # Configurable query strategies
        self.strategies = strategies or [
            "drug_symptoms",
            "drug_adverse_reactions",
            "dosage_frequency"
        ]

    def build_queries(self, entities: Dict[str, Any]) -> List[str]:
        """
        Converts extracted entities into retrieval-friendly queries based on configured strategies.
        """
        queries = []

        drugs = entities.get('drug_names', [])
        symptoms = entities.get('symptoms', [])
        dosage = entities.get('dosage', [])
        frequency = entities.get('frequency', [])

        for strategy in self.strategies:
            if strategy == "drug_symptoms":
                for drug in drugs:
                    if symptoms:
                        query = f"{drug} {' '.join(symptoms)}"
                        queries.append(query)

            elif strategy == "drug_adverse_reactions":
                for drug in drugs:
                    query = f"{drug} adverse reactions"
                    queries.append(query)

            elif strategy == "dosage_frequency":
                for d in dosage:
                    for f in frequency:
                        query = f"{d} {f}"
                        queries.append(query)

        # Ensure unique queries while preserving order
        unique_queries = []
        seen = set()
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)

        return unique_queries
