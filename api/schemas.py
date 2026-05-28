from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class ClinicalNoteRequest(BaseModel):
    clinical_note: str = Field(..., description="The clinical note text to process.")

class ClinicalOutputResponse(BaseModel):
    structured_output: Dict[str, Any]
    safety_decisions: Dict[str, Any]
    aggregated_evidence: Dict[str, Any]
    raw_ranking_results: Dict[str, Any]

class ValidationResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class IndexRebuildResponse(BaseModel):
    status: str
    message: str
