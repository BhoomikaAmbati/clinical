import logging
from typing import Dict, Any, List

from clinical.entity_extractor import ClinicalEntityExtractor
from clinical.query_builder import ClinicalQueryBuilder
from retrieval.index_manager import IndexManager
from retrieval.fusion_pipeline import FusionPipeline
from scoring.metadata_score import MetadataScorer
from retrieval.reranker import ContextualReranker
from scoring.confidence_score import ConfidenceScorer

logger = logging.getLogger(__name__)

class RankingPipeline:
    def __init__(self, index_manager: IndexManager = None):
        """
        Orchestrates the entire ranking flow:
        Extraction -> Query Generation -> Retrieval -> Fusion ->
        Metadata Scoring -> Reranking -> Confidence Calculation -> Final Ranking.
        """
        self.extractor = ClinicalEntityExtractor()
        self.query_builder = ClinicalQueryBuilder()

        # Retrieval components
        self.index_manager = index_manager or IndexManager()
        self.index_manager.load_all()

        # Pipeline components
        self.fusion = FusionPipeline()
        self.metadata_scorer = MetadataScorer()
        self.reranker = ContextualReranker()
        self.confidence_scorer = ConfidenceScorer()

    def process(self, clinical_note: str) -> Dict[str, Any]:
        logger.info("Starting Ranking Pipeline")

        # 1. Extraction
        entities = self.extractor.extract(clinical_note)
        logger.info(f"Extracted entities: {entities}")

        # 2. Query Generation
        queries = self.query_builder.build_queries(entities)
        logger.info(f"Generated queries: {queries}")

        if not queries:
            logger.warning("No queries generated. Proceeding with original note as query.")
            queries = [clinical_note]

        # 3. Retrieval
        all_bm25_results = []
        all_semantic_results = []

        for query in queries:
            res = self.index_manager.retrieve_all(query, top_k=5)
            all_bm25_results.extend(res.get("bm25", []))
            all_semantic_results.extend(res.get("semantic", []))

        retrieval_results = {
            "bm25": all_bm25_results,
            "semantic": all_semantic_results
        }
        logger.info(f"Total retrieved chunks across queries: BM25({len(all_bm25_results)}), Semantic({len(all_semantic_results)})")

        # 4. Fusion
        fusion_output = self.fusion.run(retrieval_results)
        fused_chunks = fusion_output.get("deduplicated_results", [])
        logger.info(f"Fusion complete. {len(fused_chunks)} unique chunks.")

        if not fused_chunks:
            return {
                "clinical_note": clinical_note,
                "entities": entities,
                "queries": queries,
                "ranked_chunks": []
            }

        # 5. Metadata Scoring
        for chunk in fused_chunks:
            metadata_res = self.metadata_scorer.score(entities, chunk)
            chunk["metadata_score"] = metadata_res["metadata_score"]
            chunk["matched_features"] = metadata_res["matched_features"]

        # 6. Reranking
        combined_query = " ".join(queries) if queries else clinical_note
        reranked_chunks = self.reranker.rerank(combined_query, fused_chunks)

        # 7. Confidence Calculation
        for chunk in reranked_chunks:
            fusion_score = chunk.get("score", chunk.get("rrf_score", 0.0))
            metadata_score = chunk.get("metadata_score", 0.0)
            reranker_score = chunk.get("reranker_score", 1.0)

            conf_res = self.confidence_scorer.calculate(fusion_score, metadata_score, reranker_score)
            chunk["confidence_score"] = conf_res["confidence_score"]

        # 8. Final Ranking based on confidence score
        final_ranked_chunks = sorted(reranked_chunks, key=lambda x: x.get("confidence_score", 0.0), reverse=True)
        logger.info(f"Final ranking complete for {len(final_ranked_chunks)} chunks.")

        return {
            "clinical_note": clinical_note,
            "entities": entities,
            "queries": queries,
            "ranked_chunks": final_ranked_chunks
        }
