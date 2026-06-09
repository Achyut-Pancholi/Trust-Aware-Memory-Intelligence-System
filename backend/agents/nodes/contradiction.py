from backend.agents.state import AgentState
from backend.database.db import SessionLocal
from backend.database.repository import get_memory_entries_by_subject_predicate

def detect_contradiction_node(state: AgentState) -> AgentState:
    extracted = state.get("extracted_data")
    if not extracted:
        return {**state, "contradictions": []}

    subject = extracted.get("subject")
    predicate = extracted.get("predicate")
    current_object = extracted.get("object")
    
    db = SessionLocal()
    try:
        existing_entries = get_memory_entries_by_subject_predicate(db, subject, predicate)
        
        contradictions = []
        for entry in existing_entries:
            # Check if objects differ
            if entry.object != current_object:
                contradictions.append({
                    "id": entry.id,
                    "existing_object": entry.object,
                    "confidence": entry.confidence,
                    "status": entry.status.value,
                    "type": "CONFLICT"
                })
            else:
                contradictions.append({
                    "id": entry.id,
                    "existing_object": entry.object,
                    "confidence": entry.confidence,
                    "status": entry.status.value,
                    "type": "DUPLICATE_OR_CORROBORATION"
                })
                
        return {**state, "contradictions": contradictions}
        
    finally:
        db.close()
