import logging
from typing import Dict, Any

from pipeline.ranking_pipeline import RankingPipeline
from clinical.evidence_aggregator import EvidenceAggregator
from clinical.safety_logic import SafetyLogic
from clinical.output_generator import StructuredOutputGenerator

logger = logging.getLogger(__name__)

class ClinicalPipeline:
    def __init__(self, index_manager=None):
        self.ranking_pipeline = RankingPipeline(index_manager=index_manager)
        self.evidence_aggregator = EvidenceAggregator()
        self.safety_logic = SafetyLogic()
        self.output_generator = StructuredOutputGenerator()

    def process(self, clinical_note: str) -> Dict[str, Any]:
        """
        End-to-end processing of a clinical note:
        1. Ranking Pipeline (extraction, retrieval, fusion, reranking, confidence)
        2. Evidence Aggregation
        3. Safety Logic
        4. Structured Output Generation
        """
        logger.info("Starting Clinical Pipeline")

        # 1. Ranking Pipeline
        ranking_results = self.ranking_pipeline.process(clinical_note)
        ranked_chunks = ranking_results.get("ranked_chunks", [])
        entities = ranking_results.get("entities", {})

        # 2. Evidence Aggregation
        aggregated_evidence = self.evidence_aggregator.aggregate(ranked_chunks)

        # 3. Safety Logic
        safety_decisions = self.safety_logic.infer(clinical_note, entities, aggregated_evidence)

        # 4. Structured Output Generation
        structured_output = self.output_generator.generate(entities, safety_decisions, aggregated_evidence)

        logger.info("Clinical Pipeline complete")

        return {
            "structured_output": structured_output,
            "safety_decisions": safety_decisions,
            "aggregated_evidence": aggregated_evidence,
            "raw_ranking_results": ranking_results
        }
