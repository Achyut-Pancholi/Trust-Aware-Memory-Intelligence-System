from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from backend.database.models import MemoryStatus, ActionType

class ClaimInput(BaseModel):
    id: str = Field(description="Unique ID for the incoming claim")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    source_id: str = Field(description="Name or ID of the source")
    source_reliability: float = Field(ge=0.0, le=1.0, description="Reliability score of the source (0.0 to 1.0)")
    verifiable: str = Field(description="Verifiability label, e.g., 'VERIFIABLE'")
    label: str = Field(description="Claim label, e.g., 'SUPPORTS' or 'REFUTES'")
    claim: str = Field(description="The actual natural language claim text")
    subject: str = Field(description="Extracted subject")
    predicate: str = Field(description="Extracted predicate")
    object: str = Field(description="Extracted object")

class MemoryEntryResponse(BaseModel):
    id: str
    subject: str
    predicate: str
    object: str
    confidence: float
    status: MemoryStatus
    sources: List[Dict[str, Any]]
    first_seen: datetime
    last_updated: datetime
    corroboration_count: int

    class Config:
        from_attributes = True

class ChangeLogResponse(BaseModel):
    id: str
    claim_id: str
    memory_id: Optional[str]
    timestamp: datetime
    action: ActionType
    reason: str
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    confidence_delta: float

    class Config:
        from_attributes = True

class ExplainabilityResponse(BaseModel):
    memory_id: str
    claim_text: str
    supporting_sources: List[Dict[str, Any]]
    contradicting_sources: List[Dict[str, Any]]
    current_confidence: float
    reason: str
    timeline: List[ChangeLogResponse]
