import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from backend.agents.state import AgentState
from backend.agents.prompts import CURATOR_PROMPT
from backend.core.config import settings
from backend.database.db import SessionLocal
from backend.database.models import MemoryEntry, ChangeLog, MemoryStatus, ActionType

def curate_memory_node(state: AgentState) -> AgentState:
    claim = state["claim"]
    extracted = state.get("extracted_data", {})
    verification = state.get("verification_result", {})
    trust_score = state.get("trust_score", 0.0)
    contradictions = state.get("contradictions", [])
    
    # Use LLM to decide action
    decision = {
        "action": "ACCEPTED",
        "reason": "Default action due to fallback",
        "confidence_delta": trust_score
    }
    
    if settings.GROQ_API_KEY:
        try:
            from backend.core.llm_helper import invoke_llm_with_retry
            llm = ChatGroq(temperature=0, model_name=settings.LLM_MODEL, groq_api_key=settings.GROQ_API_KEY)
            prompt = PromptTemplate.from_template(CURATOR_PROMPT)
            chain = prompt | llm
            
            response = invoke_llm_with_retry(chain, {
                "claim": claim.dict(),
                "extracted": extracted,
                "verification": verification,
                "trust_score": trust_score,
                "contradictions": contradictions
            })
            
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            decision = json.loads(content)
        except Exception as e:
            print(f"Curator LLM failed: {e}")
            decision["reason"] = f"Fallback due to error: {str(e)}"
            
    # Now, apply decision to Database
    db = SessionLocal()
    try:
        action_str = decision.get("action", "ACCEPTED")
        try:
            action_type = ActionType[action_str]
        except KeyError:
            action_type = ActionType.ACCEPTED
            
        subject = extracted.get("subject", claim.subject)
        predicate = extracted.get("predicate", claim.predicate)
        obj = extracted.get("object", claim.object)
        
        memory_id = None
        old_value = None
        new_value = {"subject": subject, "predicate": predicate, "object": obj, "confidence": trust_score}
        
        if action_type in [ActionType.ACCEPTED]:
            # Create new Memory
            entry = MemoryEntry(
                subject=subject,
                predicate=predicate,
                object=obj,
                confidence=trust_score,
                status=MemoryStatus.ACTIVE,
                sources=[{"source_id": claim.source_id, "reliability": claim.source_reliability}]
            )
            db.add(entry)
            db.flush()
            memory_id = entry.id
            
        elif action_type in [ActionType.UPDATED, ActionType.DOWNGRADED, ActionType.MERGED, ActionType.FORGOTTEN]:
            # Find the existing entry (simplification: grab the first conflict or duplicate)
            if contradictions:
                target_id = contradictions[0]["id"]
                entry = db.query(MemoryEntry).filter(MemoryEntry.id == target_id).first()
                if entry:
                    old_value = {
                        "subject": entry.subject,
                        "predicate": entry.predicate,
                        "object": entry.object,
                        "confidence": entry.confidence,
                        "status": entry.status.value if entry.status else None
                    }
                    memory_id = entry.id
                    
                    if action_type == ActionType.UPDATED:
                        entry.object = obj
                        entry.confidence = min(1.0, entry.confidence + decision.get("confidence_delta", 0.05))
                        entry.corroboration_count += 1
                        # Add source if not present
                        if not any(s.get("source_id") == claim.source_id for s in entry.sources):
                            entry.sources = entry.sources + [{"source_id": claim.source_id, "reliability": claim.source_reliability}]
                    
                    elif action_type == ActionType.MERGED:
                        entry.object = obj
                        entry.confidence = min(1.0, entry.confidence + decision.get("confidence_delta", 0.05))
                        entry.corroboration_count += 1
                        if not any(s.get("source_id") == claim.source_id for s in entry.sources):
                            entry.sources = entry.sources + [{"source_id": claim.source_id, "reliability": claim.source_reliability}]
                    
                    elif action_type == ActionType.DOWNGRADED:
                        entry.confidence = max(0.0, entry.confidence - abs(decision.get("confidence_delta", 0.1)))
                        if entry.confidence < 0.2:
                            entry.status = MemoryStatus.FORGOTTEN
                        elif entry.confidence < 0.5:
                            entry.status = MemoryStatus.LOW_CONFIDENCE

                    elif action_type == ActionType.FORGOTTEN:
                        entry.confidence = 0.0
                        entry.status = MemoryStatus.FORGOTTEN
                            
            if not memory_id:
                # Fallback if no target found
                action_type = ActionType.REJECTED
                
        elif action_type == ActionType.REJECTED:
            # We don't save a MemoryEntry, just the ChangeLog
            pass

        # Create ChangeLog
        log_entry = ChangeLog(
            claim_id=claim.id,
            memory_id=memory_id,
            action=action_type,
            reason=decision.get("reason", ""),
            old_value=old_value,
            new_value=new_value,
            confidence_delta=decision.get("confidence_delta", 0.0)
        )
        db.add(log_entry)
        db.commit()
        
        decision["action"] = action_type.value
        return {**state, "curator_decision": decision}
        
    except Exception as e:
        db.rollback()
        return {**state, "error": str(e)}
    finally:
        db.close()
