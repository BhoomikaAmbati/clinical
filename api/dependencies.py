import logging
from typing import Optional

from retrieval.index_manager import IndexManager
from pipeline.clinical_pipeline import ClinicalPipeline

logger = logging.getLogger(__name__)

# Global instances
_index_manager: Optional[IndexManager] = None
_clinical_pipeline: Optional[ClinicalPipeline] = None

def init_pipelines():
    """Initializes and loads the pipelines and indexes."""
    global _index_manager, _clinical_pipeline

    logger.info("Initializing IndexManager...")
    _index_manager = IndexManager()

    # Try loading existing indexes
    try:
        _index_manager.load_all()
    except Exception as e:
        logger.warning(f"Failed to load existing indexes, they might not exist yet: {e}")

    logger.info("Initializing ClinicalPipeline...")
    _clinical_pipeline = ClinicalPipeline(index_manager=_index_manager)

def get_index_manager() -> IndexManager:
    """Returns the shared IndexManager instance."""
    if _index_manager is None:
        logger.warning("IndexManager accessed before initialization. Initializing now.")
        init_pipelines()
    return _index_manager

def get_clinical_pipeline() -> ClinicalPipeline:
    """Returns the shared ClinicalPipeline instance."""
    if _clinical_pipeline is None:
        logger.warning("ClinicalPipeline accessed before initialization. Initializing now.")
        init_pipelines()
    return _clinical_pipeline
