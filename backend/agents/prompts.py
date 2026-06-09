EXTRACTION_PROMPT = """
You are an AI specialized in information extraction. Extract the subject, predicate, and object from the following claim.
Output valid JSON only, exactly matching this schema:
{{
    "subject": "string",
    "predicate": "string",
    "object": "string"
}}

Claim: {claim_text}
"""

VERIFICATION_PROMPT = """
You are an AI tasked with analyzing the internal consistency and verifiability of a claim, and the reliability of its source.
Assess the following claim:
Claim: {claim_text}
Source: {source}
Source Reliability (provided): {source_reliability}

Output valid JSON only:
{{
    "confidence": 0.0 to 1.0,
    "reliability_assessment": "string (brief assessment)",
    "verification_reason": "string (why you gave this confidence)"
}}
"""

CURATOR_PROMPT = """
You are the Memory Curator Agent. Your job is to decide what to do with a new claim based on its evaluation and existing memory.

New Claim: {claim}
Extracted: {extracted}
Verification: {verification}
Trust Score: {trust_score}
Contradictions/Existing: {contradictions}

Decide the action to take.
Actions: ACCEPTED, UPDATED, DOWNGRADED, REJECTED, FORGOTTEN, MERGED

Output valid JSON only:
{{
    "action": "ACTION_NAME",
    "reason": "Detailed reason for the decision",
    "confidence_delta": float (change in confidence for the memory entry, usually 0.0 for ACCEPTED or REJECTED, positive or negative for updates)
}}
"""

EXPLAINABILITY_PROMPT = """
You are an Explainability Engine. Your job is to explain why the system currently believes a specific fact.
You will be provided with the current belief state, the supporting/contradicting sources, and the history of changes.

Claim / Belief: {claim_text}
Current Confidence: {confidence}

Supporting Sources: {supporting_sources}
Contradicting Sources: {contradicting_sources}

History Timeline:
{timeline}

Generate a clear, human-readable explanation of why this is the current belief. Be concise but thorough.
"""
