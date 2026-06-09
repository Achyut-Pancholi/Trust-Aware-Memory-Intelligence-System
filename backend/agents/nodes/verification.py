import json
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from langchain_core.prompts import PromptTemplate
from backend.agents.state import AgentState
from backend.agents.prompts import VERIFICATION_PROMPT
from backend.core.config import settings

def verify_claim_node(state: AgentState) -> AgentState:
    claim = state["claim"]
    
    if not settings.GROQ_API_KEY:
        # Fallback
        return {
            **state,
            "verification_result": {
                "confidence": claim.source_reliability,
                "reliability_assessment": "Assumed reliable (fallback)",
                "verification_reason": "No API key, fallback to source reliability"
            }
        }

    try:
        llm = ChatGroq(temperature=0, model_name=settings.LLM_MODEL, groq_api_key=settings.GROQ_API_KEY)
        prompt = PromptTemplate.from_template(VERIFICATION_PROMPT)
        chain = prompt | llm
        
        response = chain.invoke({
            "claim_text": claim.claim,
            "source": claim.source_id,
            "source_reliability": claim.source_reliability
        })
        
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        verification = json.loads(content)
        
        return {**state, "verification_result": verification}
        
    except Exception as e:
        print(f"Verification failed: {e}")
        return {
            **state,
            "verification_result": {
                "confidence": claim.source_reliability,
                "reliability_assessment": "Failed to assess via LLM",
                "verification_reason": str(e)
            }
        }
