from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.db import get_db
from backend.database.repository import (
    get_all_memory_entries, get_memory_entry_by_id, 
    get_all_changelogs, get_dashboard_stats
)
from backend.schemas.pydantic_models import ClaimInput, MemoryEntryResponse, ChangeLogResponse, ExplainabilityResponse
from backend.agents.workflow import process_claim_workflow
from backend.services.explainability import generate_explanation

router = APIRouter()

@router.post("/claims")
def submit_claim(claim: ClaimInput):
    # Process through LangGraph
    final_state = process_claim_workflow(claim)
    if final_state.get("error"):
        raise HTTPException(status_code=500, detail=final_state["error"])
    
    decision = final_state.get("curator_decision", {})
    return {"message": "Claim processed successfully", "action": decision.get("action")}

@router.post("/claims/bulk")
def submit_claims_bulk(claims: List[ClaimInput]):
    results = []
    for claim in claims:
        state = process_claim_workflow(claim)
        results.append({
            "claim_id": claim.id,
            "action": state.get("curator_decision", {}).get("action"),
            "error": state.get("error")
        })
    return {"processed": len(claims), "results": results}

@router.get("/memory", response_model=List[MemoryEntryResponse])
def get_memory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_memory_entries(db, skip=skip, limit=limit)

@router.get("/memory/{id}", response_model=MemoryEntryResponse)
def get_memory_by_id(id: str, db: Session = Depends(get_db)):
    entry = get_memory_entry_by_id(db, id)
    if not entry:
        raise HTTPException(status_code=404, detail="Memory not found")
    return entry

@router.get("/memory/{id}/explain")
def explain_memory(id: str, db: Session = Depends(get_db)):
    explanation = generate_explanation(db, id)
    if "error" in explanation:
        raise HTTPException(status_code=404, detail=explanation["error"])
    return explanation

@router.get("/changelog", response_model=List[ChangeLogResponse])
def get_changelog(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_changelogs(db, skip=skip, limit=limit)

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    return get_dashboard_stats(db)

@router.post("/reset")
def reset_database_endpoint(db: Session = Depends(get_db)):
    from backend.database.repository import clear_database
    clear_database(db)
    return {"message": "Database reset successfully"}

