import json
import logging
from pipeline.clinical_pipeline import ClinicalPipeline

logging.basicConfig(level=logging.INFO)

def test_clinical_pipeline():
    clinical_note = """
    A 45-year-old male patient weighing 80 kg was admitted to the emergency room with severe dizziness,
    shortness of breath, and visual disturbances. The patient has a history of rheumatoid arthritis and
    was prescribed Actemra. He was given a dosage of 600 mg intravenously once daily.
    The hospitalization was deemed necessary due to life-threatening complications.
    """

    pipeline = ClinicalPipeline()
    results = pipeline.process(clinical_note)

    print("\n" + "="*50)
    print("Clinical Note:")
    print(clinical_note.strip())

    print("\n" + "="*50)
    print("Aggregated Evidence:")
    print(json.dumps(results["aggregated_evidence"], indent=2))

    print("\n" + "="*50)
    print("Safety Decisions:")
    print(json.dumps(results["safety_decisions"], indent=2))

    print("\n" + "="*50)
    print("Structured Output:")
    print(json.dumps(results["structured_output"], indent=2))

    print("\n" + "="*50)
    print("Top Matched PI Results:")
    for pi_result in results["structured_output"]["matched_pi_results"]:
        print(f"PI: {pi_result['pi_name']}, Confidence: {pi_result['confidence_score']:.4f}")
        for section in pi_result['matched_sections'][:3]:  # Print first 3 sections for brevity
            print(f"  - Section: {section['section_name']}")
            print(f"    Text: {section['merged_text'][:100]}...")

if __name__ == "__main__":
    test_clinical_pipeline()
