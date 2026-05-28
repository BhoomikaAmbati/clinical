import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class EvidenceAggregator:
    def __init__(self):
        pass

    def aggregate(self, ranked_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate ranked chunks into evidence groups.
        Requirements:
        * combine evidence from same PI (source_file)
        * merge repeated sections
        * preserve contributing chunk references
        * aggregate confidence
        """
        if not ranked_chunks:
            return {"drug": "", "evidence_groups": []}

        # We can extract the drug from the chunks, they should all be roughly related or we group by it.
        # But wait, ranked_chunks can come from multiple PIs and drugs.
        # Let's group by source_file (PI).
        pi_groups = {}

        main_drug = ""

        for chunk in ranked_chunks:
            source_file = chunk.get("source_file", "unknown_pi")
            drug = chunk.get("drug", "")

            if not main_drug and drug:
                main_drug = drug

            if source_file not in pi_groups:
                pi_groups[source_file] = {
                    "pi_name": source_file,
                    "confidence_score": 0.0,
                    "sections": {},
                    "chunk_refs": []
                }

            group = pi_groups[source_file]

            # Aggregate confidence score (we can take the maximum)
            confidence = chunk.get("confidence_score", 0.0)
            if confidence > group["confidence_score"]:
                group["confidence_score"] = confidence

            # Preserve chunk reference
            chunk_id = chunk.get("chunk_id")
            if chunk_id and chunk_id not in group["chunk_refs"]:
                group["chunk_refs"].append(chunk_id)

            # Merge repeated sections
            section = chunk.get("section", "unknown_section")
            text = chunk.get("text", "")

            if section not in group["sections"]:
                group["sections"][section] = []

            if text and text not in group["sections"][section]:
                group["sections"][section].append(text)

        # Format evidence groups
        evidence_groups = []
        for source_file, group_data in pi_groups.items():
            matched_sections = []
            for section_name, texts in group_data["sections"].items():
                matched_sections.append({
                    "section_name": section_name,
                    "merged_text": " ".join(texts)
                })

            evidence_groups.append({
                "pi_name": group_data["pi_name"],
                "confidence_score": group_data["confidence_score"],
                "matched_sections": matched_sections,
                "chunk_refs": group_data["chunk_refs"]
            })

        return {
            "drug": main_drug,
            "evidence_groups": evidence_groups
        }
