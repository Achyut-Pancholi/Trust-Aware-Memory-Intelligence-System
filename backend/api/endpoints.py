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
from pydantic import BaseModel

class ChatQuery(BaseModel):
    query: str

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

@router.post("/chat")
def chat_with_memory(chat_query: ChatQuery, db: Session = Depends(get_db)):
    memories = get_all_memory_entries(db, skip=0, limit=200)
    
    from backend.core.config import settings
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage
    
    memory_context = "\n".join([f"- {m.subject} {m.predicate} {m.object} (Confidence: {m.confidence:.2f}, Sources: {m.sources})" for m in memories])
    
    prompt = f"""You are a helpful and highly accurate AI assistant running on a "Trust-Aware Memory" system.
Your memory database contains verified facts.
Answer the user's question using ONLY the facts provided below.
If the facts don't contain the answer or the context is empty, say "I don't have verified information regarding that."
DO NOT hallucinate external knowledge. Always cite the confidence score and sources if you provide an answer.

VERIFIED FACTS:
{memory_context}

USER QUESTION:
{chat_query.query}
"""
    try:
        llm = ChatGroq(temperature=0, model_name=settings.LLM_MODEL, groq_api_key=settings.GROQ_API_KEY)
        response = llm.invoke([HumanMessage(content=prompt)])
        return {"answer": response.content}
    except Exception as e:
        return {"answer": f"Error generating response: {str(e)}"}

