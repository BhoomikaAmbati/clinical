import re
import logging
from typing import Dict, Any, List, Optional
from clinical.normalizer import ClinicalNormalizer

logger = logging.getLogger(__name__)

class ClinicalEntityExtractor:
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        self.normalizer = ClinicalNormalizer()

        # Default extraction rules
        self.rules = rules or {
            'drug_names': [r'\b(Metformin|Actemra|Lucentis|Ocrevus|Lisinopril|Aspirin|Ibuprofen)\b'],
            'symptoms': [r'\b(dizziness|nausea|headache|fever|fatigue|pain|swelling|rash|cough)\b'],
            'dosage': [r'\b(\d+(?:\.\d+)?\s*(?:mg|ml|mcg|g|kg|lbs?))\b'],
            'frequency': [r'\b(BID|TID|QID|QD|QHS|PRN|twice daily|once daily|every \d+ hours)\b'],
            'route': [r'\b(PO|IV|IM|SQ|by mouth|intravenously|subcutaneously|intramuscularly)\b'],
            'age': [r'\b(\d+)\s*(?:years?|yrs?|yo)\s*(?:old)?\b'],
            'weight': [r'\b(\d+(?:\.\d+)?)\s*(?:kg|lbs?)\b'],
            'population': [r'\b(pediatric|adult|geriatric|pregnant|infant|elderly)\b'],
            'temporal': [r'\b(yesterday|today|tomorrow|last week|next week|\d+ days ago)\b'],
            'hospitalization': [r'\b(admitted|hospitalized|discharge|inpatient)\b'],
            'seriousness': [r'\b(severe|mild|moderate|life-threatening|critical)\b'],
            'j_codes': [r'\b(J\d{4})\b'],
            'icd_codes': [r'\b([A-Z]\d{2}(?:\.\d{1,4})?)\b']
        }

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extracts entities from free text clinical notes or voice transcriptions.
        Returns a dictionary with exactly the requested keys.
        """
        result = {
            "drug_names": [],
            "symptoms": [],
            "dosage": [],
            "frequency": [],
            "route": [],
            "age": None,
            "weight": None,
            "population": [],
            "temporal": [],
            "hospitalization": None,
            "seriousness": [],
            "j_codes": [],
            "icd_codes": []
        }

        if not text:
            return result

        logger.debug(f"Extracting entities from text of length {len(text)}")

        for entity_type, patterns in self.rules.items():
            extracted_items = []
            for pattern in patterns:
                # Case-insensitive extraction
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    extracted_items.append(match.group(0))

            if entity_type in ['age', 'weight', 'hospitalization']:
                if extracted_items:
                    # Take the first match for singular values
                    result[entity_type] = extracted_items[0]
            else:
                result[entity_type] = extracted_items

        # Apply normalization
        normalized_result = self.normalizer.normalize_entities(result)

        # Ensure age, weight, hospitalization remain as None if empty list after normalization logic
        for key in ['age', 'weight', 'hospitalization']:
            if not normalized_result[key]:
                normalized_result[key] = None

        return normalized_result
