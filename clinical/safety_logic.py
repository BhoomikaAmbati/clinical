import logging
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)

class SafetyLogic:
    def __init__(self):
        # Configurable rules
        self.seriousness_indicators = [
            r'\ber\b', r'\bemergency room\b', r'\bemergency department\b',
            r'\bicu\b', r'\bintensive care\b', r'\bdeath\b', r'\bdied\b',
            r'\bfatal\b', r'\blife[- ]threatening\b', r'\bdisability\b'
        ]

        self.hospitalization_indicators = [
            r'\badmitted\b', r'\bhospitalized\b', r'\bhospitalization\b',
            r'\binpatient\b'
        ]

    def _check_indicators(self, text: str, indicators: List[str]) -> List[str]:
        found = []
        if not text:
            return found

        text_lower = text.lower()
        for indicator in indicators:
            if re.search(indicator, text_lower):
                found.append(indicator.replace('\\b', ''))
        return found

    def infer(self, clinical_note: str, entities: Dict[str, Any], aggregated_evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infer safety logic decisions.
        """
        seriousness = []
        hospitalization = False
        possible_relatedness = False
        black_box_relevance = False

        note = clinical_note.lower() if clinical_note else ""

        # 1. Infer Hospitalization
        # Based on entities
        if entities.get('hospitalization'):
            hospitalization = True

        # Based on note content matching indicators
        if not hospitalization:
            hosp_matches = self._check_indicators(note, self.hospitalization_indicators)
            if hosp_matches:
                hospitalization = True

        # 2. Infer Seriousness
        # From entities
        entity_seriousness = entities.get('seriousness', [])
        if entity_seriousness:
            if isinstance(entity_seriousness, list):
                seriousness.extend(entity_seriousness)
            else:
                seriousness.append(str(entity_seriousness))

        # From note
        serious_matches = self._check_indicators(note, self.seriousness_indicators)
        for match in serious_matches:
            if match not in seriousness:
                seriousness.append(match)

        if hospitalization and "hospitalization" not in seriousness:
            seriousness.append("hospitalization")

        # 3. Infer Possible relatedness
        # Are there any symptoms overlapping with evidence?
        symptoms = entities.get('symptoms', [])
        evidence_groups = aggregated_evidence.get('evidence_groups', [])

        if symptoms and evidence_groups:
            for group in evidence_groups:
                for section in group.get('matched_sections', []):
                    section_text = section.get('merged_text', '').lower()
                    for symptom in symptoms:
                        if symptom.lower() in section_text:
                            possible_relatedness = True
                            break
                    if possible_relatedness:
                        break
                if possible_relatedness:
                    break

        # 4. Infer Black box relevance
        # Are there any black box sections in evidence?
        if evidence_groups:
            for group in evidence_groups:
                for section in group.get('matched_sections', []):
                    if 'boxed warning' in section.get('section_name', '').lower() or 'black box' in section.get('section_name', '').lower():
                        black_box_relevance = True
                        break
                if black_box_relevance:
                    break

        return {
            "seriousness": seriousness,
            "hospitalization": hospitalization,
            "possible_relatedness": possible_relatedness,
            "black_box_relevance": black_box_relevance
        }
