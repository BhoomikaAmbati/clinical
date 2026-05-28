import logging
import difflib
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DuplicateReducer:
    def __init__(self, similarity_threshold: float = 0.9):
        """
        :param similarity_threshold: SequenceMatcher ratio above which two chunk texts
                                     are considered nearly identical.
        """
        self.similarity_threshold = similarity_threshold

    def is_duplicate(self, chunk_a: Dict[str, Any], chunk_b: Dict[str, Any]) -> bool:
        """
        Determines if chunk_b is a duplicate of chunk_a based on:
        - identical text
        - nearly identical text
        - repeated sections (same section and source_file)
        """
        text_a = chunk_a.get("text", "")
        text_b = chunk_b.get("text", "")

        # 1. Identical chunk text
        if text_a == text_b:
            return True

        # 2. Repeated sections (same section and source_file)
        # Assuming we don't want to consider chunks as duplicates just because they
        # belong to the same section, BUT requirement says:
        # "repeated sections (matching `section` and `source_file` metadata)"
        # So we'll check if they have the exact same section and source_file
        section_a = chunk_a.get("section")
        section_b = chunk_b.get("section")
        source_a = chunk_a.get("source_file")
        source_b = chunk_b.get("source_file")

        if section_a and section_b and source_a and source_b:
            if section_a == section_b and source_a == source_b:
                return True

        # 3. Nearly identical chunk text
        if self.similarity_threshold < 1.0:
            similarity = difflib.SequenceMatcher(None, text_a, text_b).ratio()
            if similarity >= self.similarity_threshold:
                return True

        return False

    def reduce(self, ranked_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Reduces duplicate evidence from a list of ranked chunks.
        Expects ranked_results to be sorted in descending order of score,
        so it keeps the highest-scoring ones first.

        :param ranked_results: A list of dicts output by RRFusion.fuse()
        :return: A deduplicated list of dicts.
        """
        deduplicated = []
        reduced_count = 0

        for item in ranked_results:
            chunk = item.get("chunk", {})

            is_dup = False
            for kept_item in deduplicated:
                kept_chunk = kept_item.get("chunk", {})
                if self.is_duplicate(kept_chunk, chunk):
                    is_dup = True
                    break

            if not is_dup:
                deduplicated.append(item)
            else:
                reduced_count += 1

        logger.info(f"Duplicate reduction removed {reduced_count} duplicate chunks.")

        return deduplicated
