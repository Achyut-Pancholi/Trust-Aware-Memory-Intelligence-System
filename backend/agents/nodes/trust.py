from backend.agents.state import AgentState

def calculate_trust_score_node(state: AgentState) -> AgentState:
    claim = state["claim"]
    verification = state.get("verification_result", {})
    contradictions = state.get("contradictions", [])
    
    # 0.4 * source_reliability
    source_reliability = claim.source_reliability
    
    # 0.3 * corroboration_score
    corroborations = [c for c in contradictions if c["type"] == "DUPLICATE_OR_CORROBORATION"]
    corroboration_score = min(1.0, len(corroborations) * 0.2 + 0.5 if corroborations else 0.5)
    
    # 0.2 * recency_score (Simplification: assuming new claims are recent=1.0 unless stale)
    recency_score = 1.0 
    
    # 0.1 * consistency_score 
    # If there are conflicts, consistency drops
    conflicts = [c for c in contradictions if c["type"] == "CONFLICT"]
    consistency_score = 1.0 if not conflicts else max(0.0, 1.0 - (len(conflicts) * 0.3))
    
    trust_score = (0.4 * source_reliability) + (0.3 * corroboration_score) + (0.2 * recency_score) + (0.1 * consistency_score)
    
    return {**state, "trust_score": trust_score}
