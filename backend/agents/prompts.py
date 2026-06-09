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
IMPORTANT: Treat announcements about future events (e.g. "Product X launches in 2026") as verifiable claims if they come from a reliable source. Do not reject claims simply because they occur in the future. Your verification confidence should heavily rely on the provided source_reliability.
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

Decide the action to take. You MUST choose one of the following Actions based on the criteria:

1. ACCEPTED: Use when there is NO existing memory matching the subject and predicate, and the claim is somewhat trustworthy (trust score >= 0.3).
2. REJECTED: Use when the new claim is completely untrustworthy (trust score < 0.2) OR the verification label is REFUTES, regardless of existing memories. We completely reject the new claim.
3. FORGOTTEN: Use when a new highly reliable claim (trust score >= 0.8) completely invalidates a weak existing memory (confidence < 0.6), indicating the old memory is completely obsolete. The existing memory will be set to forgotten.
4. DOWNGRADED: Use when the new claim contradicts the existing memory (different object) but has a LOW or MEDIUM trust score (e.g. 0.2 to 0.6). We want to keep the existing memory, but DECREASE its confidence score.
5. UPDATED: Use when the new claim has a DIFFERENT object than the existing memory, and the new claim has a HIGH trust score (>= 0.7) that is higher than or comparable to the existing memory, so we want to REPLACE the old object with the new object.
6. MERGED: Use when the new claim has the SAME or semantically identical object as the existing memory. We want to keep the memory and INCREASE its confidence.

CRITICAL RULE: If the list of Contradictions/Existing memories is empty ([]) or null, you can ONLY choose 'ACCEPTED' or 'REJECTED'. You must NEVER choose 'UPDATED', 'DOWNGRADED', 'FORGOTTEN', or 'MERGED' if there are no existing memories listed.

Output valid JSON only:
{{
    "action": "ACTION_NAME",
    "reason": "Detailed reason for the decision based on the criteria",
    "confidence_delta": float (positive float for MERGED/UPDATED/corroborations, negative float for DOWNGRADED, 0.0 for ACCEPTED/REJECTED/FORGOTTEN)
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
