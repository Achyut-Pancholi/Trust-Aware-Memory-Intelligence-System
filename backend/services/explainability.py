from sqlalchemy.orm import Session
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from backend.core.config import settings
from backend.database.repository import get_memory_entry_by_id, get_changelogs_for_memory
from backend.agents.prompts import EXPLAINABILITY_PROMPT

def generate_explanation(db: Session, memory_id: str) -> dict:
    entry = get_memory_entry_by_id(db, memory_id)
    if not entry:
        return {"error": "Memory not found"}
        
    logs = get_changelogs_for_memory(db, memory_id)
    
    # Format the current belief
    claim_text = f"{entry.subject} {entry.predicate} {entry.object}"
    
    # We simplified sources, but we can extract supporting/contradicting from logs
    # For now, all current sources in entry are supporting the current object
    supporting_sources = entry.sources
    
    # Contradicting sources can be inferred from logs where old_value object != new_value object
    # or where action was DOWNGRADED
    contradicting_sources = []
    
    timeline_str = ""
    for idx, log in enumerate(reversed(logs)):
        timeline_str += f"Step {idx+1} [{log.timestamp}]: Action={log.action.value}, Reason={log.reason}, Confidence Delta={log.confidence_delta}\n"
        if log.old_value and log.new_value and log.old_value.get("object") != log.new_value.get("object"):
            # This was a conflict/update
            pass
            
    reason = "Fallback explainability reason (No LLM)"
    if settings.GROQ_API_KEY:
        try:
            llm = ChatGroq(temperature=0, model_name=settings.LLM_MODEL, groq_api_key=settings.GROQ_API_KEY)
            prompt = PromptTemplate.from_template(EXPLAINABILITY_PROMPT)
            chain = prompt | llm
            
            response = chain.invoke({
                "claim_text": claim_text,
                "confidence": entry.confidence,
                "supporting_sources": supporting_sources,
                "contradicting_sources": contradicting_sources, # Simplified
                "timeline": timeline_str
            })
            reason = response.content
        except Exception as e:
            reason = f"LLM error: {e}"
            
    return {
        "memory_id": memory_id,
        "claim_text": claim_text,
        "supporting_sources": supporting_sources,
        "contradicting_sources": contradicting_sources,
        "current_confidence": entry.confidence,
        "reason": reason,
        "timeline": [{"id": l.id, "action": l.action.value, "reason": l.reason, "timestamp": l.timestamp.isoformat()} for l in logs]
    }
