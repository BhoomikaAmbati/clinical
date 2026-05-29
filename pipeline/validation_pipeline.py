import logging
from typing import Dict, Any, List

from config import DATA_DIR, PI_FILENAMES
from preprocessing.kb_loader import KBLoader
from preprocessing.chunker import DocumentChunker
from preprocessing.schema_inspector import SchemaInspector
from preprocessing.schema_adapter import SchemaAdapter
from retrieval.index_manager import IndexManager
from pipeline.ranking_pipeline import RankingPipeline

logger = logging.getLogger(__name__)

class ValidationPipeline:
    def __init__(self):
        self.loader = KBLoader(data_dir=DATA_DIR)
        self.chunker = DocumentChunker()
        self.inspector = SchemaInspector()
        self.adapter = SchemaAdapter()
        self.index_manager = IndexManager()
        # ranking pipeline initialized after building indexes
        self.ranking_pipeline = None

    def run(self, dummy_query: str = "test query") -> Dict[str, Any]:
        """
        Coordinates the validation pipeline:
        1. Load PI files
        2. Inspect & Adapt schema
        3. Chunk
        4. Build indexes
        5. Run retrieval & ranking
        6. Generate validation report
        """
        report = {
            "files_processed": 0,
            "schema_detected": {},
            "chunks_created": 0,
            "retrieval_success": False,
            "ranking_success": False,
            "errors": []
        }

        # 1. Load files
        try:
            documents = self.loader.load_all(PI_FILENAMES)
        except Exception as e:
            report["errors"].append(f"Failed to load documents: {e}")
            return report

        total_chunks = 0
        all_chunks = []

        # 2. & 3. Process each document
        for filename in PI_FILENAMES:
            doc = documents.get(filename)
            if not doc:
                continue

            report["files_processed"] += 1

            try:
                # Inspect Schema
                schema_summary = self.inspector.inspect(doc)
                report["schema_detected"][filename] = schema_summary

                # Chunker now internally adapts the schema and extracts chunks
                chunks = self.chunker.chunk_document(filename, doc)
                if chunks:
                    all_chunks.extend(chunks)
                    total_chunks += len(chunks)

                # Save chunks via the pipeline if needed. For validation, we
                # don't strictly need to overwrite the actual chunked dir unless
                # we want to build indexes from them.
                # Actually, IndexManager reads from `chunked` dir.
                # Since the chunker test saves them via `save_chunks`, we'll do the same.

                from preprocessing.save_chunks import save_chunks
                drug_name = self.chunker._extract_drug_name(filename)
                if chunks:
                     save_chunks(drug_name, chunks)

            except Exception as e:
                report["errors"].append(f"Error processing {filename}: {e}")

        report["chunks_created"] = total_chunks

        # 4. Build Indexes
        try:
            self.index_manager.build_all()
        except Exception as e:
            report["errors"].append(f"Failed to build indexes: {e}")
            return report

        # 5. Run Retrieval & Ranking
        try:
            # We initialize RankingPipeline here because it depends on the newly built IndexManager
            self.index_manager.load_all()
            self.ranking_pipeline = RankingPipeline(index_manager=self.index_manager)

            ranking_results = self.ranking_pipeline.process(dummy_query)

            if ranking_results and "ranked_chunks" in ranking_results:
                report["retrieval_success"] = True
                report["ranking_success"] = True
            else:
                 report["errors"].append("Ranking results were empty or malformed.")

        except Exception as e:
            report["errors"].append(f"Retrieval or ranking failed: {e}")

        return report
