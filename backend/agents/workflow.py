from langgraph.graph import StateGraph, END
from backend.agents.state import AgentState
from backend.agents.nodes.extraction import extract_claim_node
from backend.agents.nodes.verification import verify_claim_node
from backend.agents.nodes.contradiction import detect_contradiction_node
from backend.agents.nodes.trust import calculate_trust_score_node
from backend.agents.nodes.curator import curate_memory_node

def create_memory_workflow():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("extraction", extract_claim_node)
    workflow.add_node("verification", verify_claim_node)
    workflow.add_node("contradiction", detect_contradiction_node)
    workflow.add_node("trust", calculate_trust_score_node)
    workflow.add_node("curator", curate_memory_node)

    # Define edges
    workflow.set_entry_point("extraction")
    workflow.add_edge("extraction", "verification")
    workflow.add_edge("verification", "contradiction")
    workflow.add_edge("contradiction", "trust")
    workflow.add_edge("trust", "curator")
    workflow.add_edge("curator", END)

    # Compile the graph
    app = workflow.compile()
    return app

# Singleton instance
memory_workflow = create_memory_workflow()

def process_claim_workflow(claim_input):
    initial_state = {
        "claim": claim_input,
        "extracted_data": None,
        "verification_result": None,
        "contradictions": None,
        "trust_score": None,
        "curator_decision": None,
        "error": None
    }
    
    final_state = memory_workflow.invoke(initial_state)
    return final_state
