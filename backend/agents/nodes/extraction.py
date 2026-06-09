import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from backend.agents.state import AgentState
from backend.agents.prompts import EXTRACTION_PROMPT
from backend.core.config import settings

def extract_claim_node(state: AgentState) -> AgentState:
    claim = state["claim"]
    
    # If the claim already has pre-defined subject, predicate, and object (e.g. from demo data),
    # use them directly to guarantee exact matching for demo runs. Otherwise, use the LLM.
    if claim.subject and claim.predicate and claim.object:
        return {
            **state,
            "extracted_data": {
                "subject": claim.subject,
                "predicate": claim.predicate,
                "object": claim.object
            }
        }

    if not settings.GROQ_API_KEY:
        # Fallback if no API key during testing
        return {
            **state,
            "extracted_data": {
                "subject": claim.subject,
                "predicate": claim.predicate,
                "object": claim.object
            }
        }

    try:
        from backend.core.llm_helper import invoke_llm_with_retry
        llm = ChatGroq(temperature=0, model_name=settings.LLM_MODEL, groq_api_key=settings.GROQ_API_KEY)
        prompt = PromptTemplate.from_template(EXTRACTION_PROMPT)
        chain = prompt | llm
        
        response = invoke_llm_with_retry(chain, {"claim_text": claim.claim})
        
        # Parse JSON
        content = response.content
        # sometimes LLMs wrap JSON in markdown block
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        extracted = json.loads(content)
        
        return {**state, "extracted_data": extracted}
        
    except Exception as e:
        # Fallback to the provided schema fields if extraction fails
        print(f"Extraction failed: {e}")
        return {
            **state,
            "extracted_data": {
                "subject": claim.subject,
                "predicate": claim.predicate,
                "object": claim.object
            }
        }
