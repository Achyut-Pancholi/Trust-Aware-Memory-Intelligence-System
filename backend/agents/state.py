from typing import TypedDict, Optional, List, Dict, Any
from backend.schemas.pydantic_models import ClaimInput

class AgentState(TypedDict):
    claim: ClaimInput
    extracted_data: Optional[Dict[str, str]]
    verification_result: Optional[Dict[str, Any]]
    contradictions: Optional[List[Dict[str, Any]]]
    trust_score: Optional[float]
    curator_decision: Optional[Dict[str, Any]]
    error: Optional[str]
