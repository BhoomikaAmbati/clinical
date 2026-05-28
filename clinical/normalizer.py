import re
from typing import Any, Dict, List, Union

class ClinicalNormalizer:
    def __init__(self):
        self.unit_mapping = {
            r'\bMG\b': 'mg',
            r'\bML\b': 'ml',
            r'\bKG\b': 'kg',
            r'\bG\b': 'g',
            r'\bMCG\b': 'mcg',
            r'\bLBS?\b': 'lb'
        }

        self.dosage_format_mapping = {
            r'\bBID\b': 'twice daily',
            r'\bTID\b': 'three times daily',
            r'\bQID\b': 'four times daily',
            r'\bQD\b': 'once daily',
            r'\bQHS\b': 'at bedtime',
            r'\bPRN\b': 'as needed',
            r'\bPO\b': 'by mouth',
            r'\bIV\b': 'intravenously',
            r'\bIM\b': 'intramuscularly',
            r'\bSQ\b': 'subcutaneously',
            r'\bQ4H\b': 'every 4 hours',
            r'\bQ6H\b': 'every 6 hours',
            r'\bQ8H\b': 'every 8 hours',
            r'\bQ12H\b': 'every 12 hours'
        }

    def normalize_text(self, text: str) -> str:
        if not text:
            return text

        # Capitalization
        normalized = text.lower()

        # Mapping units (case-insensitive search, lowercasing mapping keys)
        for pattern, replacement in self.unit_mapping.items():
            regex = re.compile(pattern, re.IGNORECASE)
            normalized = regex.sub(replacement, normalized)

        # Mapping dosage formats
        for pattern, replacement in self.dosage_format_mapping.items():
            regex = re.compile(pattern, re.IGNORECASE)
            normalized = regex.sub(replacement, normalized)

        # Spacing
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def normalize_entities(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        normalized_entities = {}
        for key, value in entities.items():
            if isinstance(value, list):
                # Remove duplicates while preserving order
                seen = set()
                norm_list = []
                for item in value:
                    if isinstance(item, str):
                        norm_item = self.normalize_text(item)
                    else:
                        norm_item = item

                    if norm_item not in seen:
                        seen.add(norm_item)
                        norm_list.append(norm_item)
                normalized_entities[key] = norm_list
            elif isinstance(value, str):
                normalized_entities[key] = self.normalize_text(value)
            else:
                normalized_entities[key] = value

        return normalized_entities
