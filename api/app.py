import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from api.schemas import (
    ClinicalNoteRequest,
    ClinicalOutputResponse,
    IndexRebuildResponse
)
from api.dependencies import init_pipelines, get_clinical_pipeline, get_index_manager
from pipeline.clinical_pipeline import ClinicalPipeline
from retrieval.index_manager import IndexManager

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    # Startup
    logger.info("Starting up FastAPI application...")
    init_pipelines()
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application...")

app = FastAPI(
    title="Clinical Pipeline API",
    description="API for processing clinical notes and managing PI retrieval indexes.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def health_check():
    """Health endpoint."""
    return {"status": "healthy"}

@app.post("/process_note", response_model=ClinicalOutputResponse)
def process_note(
    request: ClinicalNoteRequest,
    pipeline: ClinicalPipeline = Depends(get_clinical_pipeline)
):
    """
    Process a clinical note through the end-to-end clinical pipeline.
    """
    clinical_note = request.clinical_note.strip()
    if not clinical_note:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clinical note cannot be empty."
        )

    try:
        results = pipeline.process(clinical_note)
        return ClinicalOutputResponse(**results)
    except Exception as e:
        logger.error(f"Error processing clinical note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline failure: {str(e)}"
        )

@app.post("/rebuild_indexes", response_model=IndexRebuildResponse)
def rebuild_indexes(
    index_manager: IndexManager = Depends(get_index_manager)
):
    """
    Rebuild the retrieval indexes (BM25 and Semantic).
    This assumes that chunking has already been done and chunks are in the chunked/ directory.
    To fully rebuild from PI files, we also need to trigger chunking first.
    For this implementation, we will import kb_loader and save_chunks to do it properly.
    """
    try:
        from preprocessing.kb_loader import KBLoader
        from preprocessing.chunker import DocumentChunker
        from preprocessing.save_chunks import save_chunks
        from config import DATA_DIR, PI_FILENAMES

        logger.info("Reloading PI files and rechunking...")
        loader = KBLoader(DATA_DIR)
        chunker = DocumentChunker()

        for filename in PI_FILENAMES:
            document = loader.load_document(filename)
            if not document:
                logger.warning(f"Could not load {filename}")
                continue

            chunks = chunker.chunk_document(filename, document)
            drug_name = chunker._extract_drug_name(filename)
            save_chunks(drug_name, chunks)
            logger.info(f"Saved {len(chunks)} chunks for {drug_name}")

        logger.info("Rebuilding indexes...")
        index_manager.build_all()
        # Reload indexes after building
        index_manager.load_all()

        return IndexRebuildResponse(
            status="success",
            message="Indexes rebuilt successfully."
        )
    except Exception as e:
        logger.error(f"Error rebuilding indexes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Index rebuild failure: {str(e)}"
        )
