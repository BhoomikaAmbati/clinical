import json
from clinical.entity_extractor import ClinicalEntityExtractor
from clinical.normalizer import ClinicalNormalizer
from clinical.query_builder import ClinicalQueryBuilder

def run_test():
    # Long sample clinical note (free text/voice transcription style)
    sample_text = """
    Patient is a 65 yo elderly male admitted yesterday for observation.
    He has a history of type 2 diabetes and is currently taking Metformin 500 MG BID PO.
    During the morning rounds, the patient reported experiencing severe dizziness and mild nausea
    over the last week. Weight is currently 85 KG.
    We are considering switching his medication or adjusting the dosage if the headache and rash persist.
    He may also require Actemra 162 mg SQ once daily if his condition worsens.
    """

    print("--- Original Text ---")
    print(sample_text.strip())
    print("\n")

    # Instantiate the components
    extractor = ClinicalEntityExtractor()
    query_builder = ClinicalQueryBuilder()

    # Extract entities (this internally normalizes them)
    extracted_entities = extractor.extract(sample_text)

    # For demonstration of normalizer usage directly, though the extractor does this
    normalizer = ClinicalNormalizer()
    normalized_text = normalizer.normalize_text(sample_text)

    # Print extracted (and normalized) entities
    print("--- Extracted & Normalized Entities ---")
    print(json.dumps(extracted_entities, indent=2))
    print("\n")

    # Generate queries
    queries = query_builder.build_queries(extracted_entities)

    print("--- Generated Queries ---")
    for q in queries:
        print(f"- {q}")
    print("\n")

if __name__ == "__main__":
    run_test()
