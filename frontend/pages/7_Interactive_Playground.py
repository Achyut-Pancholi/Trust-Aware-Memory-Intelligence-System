import streamlit as st
import requests
import time
import uuid

API_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="Testing Playground", page_icon="🧪", layout="wide")

# ── Inject Page CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root {
    --bg-primary: #0a0a14;
    --bg-card: rgba(22, 22, 40, 0.7);
    --glass-border: rgba(108, 92, 231, 0.15);
    --text-primary: #e8e8f0;
    --text-secondary: #9090b0;
    --accent-purple: #6C5CE7;
    --accent-green: #00b894;
    --accent-blue: #0984e3;
    --accent-red: #d63031;
    --accent-orange: #e17055;
}
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
}
.page-header {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C5CE7, #00cec9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}
.page-subtitle {
    color: var(--text-secondary);
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}
.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 1.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.card {
    background: var(--bg-card);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1.5rem;
}
.scenario-step {
    border-left: 3px solid var(--accent-purple);
    padding-left: 1rem;
    margin-bottom: 1rem;
}
.step-title {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text-primary);
}
.step-desc {
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-top: 0.2rem;
}
.step-status {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    margin-top: 0.3rem;
}
.status-pending { background: rgba(144, 144, 176, 0.15); color: #9090b0; }
.status-success { background: rgba(0, 184, 148, 0.15); color: #00b894; }
.status-error { background: rgba(214, 48, 49, 0.15); color: #d63031; }

/* Custom Buttons */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────
st.markdown('<div class="page-header">🧪 Interactive Testing Playground</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Test belief acceptance, contradiction, merges, updates, and decay live.</div>', unsafe_allow_html=True)

# ── Database Controls ───────────────────────────────────────────────────
col_reset, col_load_demo, _ = st.columns([1, 1.5, 3])

with col_reset:
    if st.button("🗑️ Reset Database", use_container_width=True):
        try:
            res = requests.post(f"{API_URL}/reset")
            if res.status_code == 200:
                st.toast("Database reset successfully!", icon="🗑️")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Failed to reset database.")
        except Exception as e:
            st.error(f"Error connecting to API: {e}")

with col_load_demo:
    if st.button("🚀 Load Comprehensive Demo Data", use_container_width=True):
        try:
            with st.spinner("Ingesting comprehensive demo data..."):
                import json
                with open("demo_data_comprehensive.json", "r") as f:
                    data = json.load(f)
                
                # Reset first
                requests.post(f"{API_URL}/reset")
                
                # Ingest bulk or individual
                ingested = 0
                for claim in data:
                    requests.post(f"{API_URL}/claims", json=claim)
                    ingested += 1
                
                st.success(f"Successfully ingested {ingested} claims! Check the Dashboard.")
                time.sleep(1.0)
                st.rerun()
        except Exception as e:
            st.error(f"Error loading demo data: {e}")

st.markdown("---")

tab1, tab2 = st.tabs(["⚡ Walkthrough Scenarios", "✍️ Submit Custom Claim"])

# ── Tab 1: Walkthrough Scenarios ────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">💡 Packaged Multi-Step Scenarios</div>', unsafe_allow_html=True)
    st.write("These packaged scenarios show how a single fact transitions through multiple states based on source reliability, contradiction, and temporal updates.")

    scenarios = {
        "Scenario 1: Belief Evolution (Accepted → Updated → Downgraded/Forgotten)": [
            {
                "id": "PLAY-S1-P1",
                "claim": "Company X launched Product Y (v1.0)",
                "source_id": "OfficialPR",
                "source_reliability": 0.95,
                "verifiable": "VERIFIABLE",
                "label": "SUPPORTS",
                "subject": "Company X",
                "predicate": "launched_product",
                "object": "Product Y",
                "expected": "ACCEPTED: High reliability source establishes the initial belief with high confidence."
            },
            {
                "id": "PLAY-S1-P2",
                "claim": "Company X updated Product Y to v2.0",
                "source_id": "TechCrunch",
                "source_reliability": 0.88,
                "verifiable": "VERIFIABLE",
                "label": "SUPPORTS",
                "subject": "Company X",
                "predicate": "launched_product",
                "object": "Product Y",
                "expected": "UPDATED/MERGED: Evolution is detected. The version update modifies the existing object."
            },
            {
                "id": "PLAY-S1-P3",
                "claim": "Company X recalls Product Y due to safety concerns",
                "source_id": "RegulatoryBoard",
                "source_reliability": 0.99,
                "verifiable": "VERIFIABLE",
                "label": "SUPPORTS",
                "subject": "Company X",
                "predicate": "product_status",
                "object": "Recalled",
                "expected": "ACCEPTED & DOWNGRADED: A regulatory authority announces a recall. The status updates, and the confidence of product success is downgraded."
            }
        ],
        "Scenario 2: Contradicting Rumors & Trust Evaluation (Rejected vs. Merged)": [
            {
                "id": "PLAY-S2-P1",
                "claim": "Apple is buying Netflix next month",
                "source_id": "SpamBot",
                "source_reliability": 0.15,
                "verifiable": "UNVERIFIABLE",
                "label": "SUPPORTS",
                "subject": "Apple",
                "predicate": "acquiring",
                "object": "Netflix",
                "expected": "REJECTED: Very low source reliability prevents creation of a memory entry."
            },
            {
                "id": "PLAY-S2-P2",
                "claim": "Apple signs content partnership with Netflix",
                "source_id": "FinancialTimes",
                "source_reliability": 0.90,
                "verifiable": "VERIFIABLE",
                "label": "SUPPORTS",
                "subject": "Apple",
                "predicate": "partners_with",
                "object": "Netflix",
                "expected": "ACCEPTED: A highly reliable publication establishes this valid business relationship."
            },
            {
                "id": "PLAY-S2-P3",
                "claim": "Apple does not partner with Netflix",
                "source_id": "TwitterRumor",
                "source_reliability": 0.35,
                "verifiable": "VERIFIABLE",
                "label": "REFUTES",
                "subject": "Apple",
                "predicate": "partners_with",
                "object": "Netflix",
                "expected": "REJECTED/IGNORED: High trust in FT partnership remains robust against a low-reliability rumor."
            }
        ]
    }

    selected_scenario_name = st.selectbox("Select a scenario to execute step-by-step:", list(scenarios.keys()))
    scenario_steps = scenarios[selected_scenario_name]

    col_s1, col_s2, col_s3 = st.columns(3)
    cols = [col_s1, col_s2, col_s3]

    for idx, step in enumerate(scenario_steps):
        with cols[idx]:
            st.markdown(f"""
            <div class="card">
                <div class="scenario-step">
                    <div class="step-title">Step {idx+1}: {step['claim']}</div>
                    <div class="step-desc"><strong>Source:</strong> {step['source_id']} ({step['source_reliability']})</div>
                    <div class="step-desc"><strong>Expected outcome:</strong> {step['expected']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Run Step {idx+1}", key=f"btn_step_{step['id']}"):
                with st.spinner("Processing through multi-agent workflow..."):
                    # Generate a unique ID to avoid duplicates
                    claim_to_send = {**step}
                    claim_to_send["id"] = f"{step['id']}-{str(uuid.uuid4())[:8]}"
                    
                    try:
                        res = requests.post(f"{API_URL}/claims", json=claim_to_send)
                        if res.status_code == 200:
                            res_data = res.json()
                            action = res_data.get("action", "UNKNOWN")
                            st.success(f"Step {idx+1} processed successfully!")
                            st.info(f"**Action taken by Curator:** {action}")
                            
                            # Let's show the change log entries related to this
                            changelog_res = requests.get(f"{API_URL}/changelog?limit=1")
                            if changelog_res.status_code == 200 and changelog_res.json():
                                last_log = changelog_res.json()[0]
                                st.markdown(f"**Curator Explanation:** {last_log.get('reason')}")
                                st.markdown(f"**Confidence Delta:** `{last_log.get('confidence_delta', 0.0):+.3f}`")
                        else:
                            st.error(f"Error {res.status_code}: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

# ── Tab 2: Submit Custom Claim ──────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">✍️ Ingest a Custom Claim</div>', unsafe_allow_html=True)
    st.write("Type a natural language claim and define the source context. Watch how the extraction agent parsing triples and curation agent evaluating trust interact.")

    with st.form("custom_claim_form"):
        claim_text = st.text_area("Claim text", placeholder="e.g., Apple is releasing an AR glasses headset in 2026")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            source_id = st.text_input("Source Identifier", value="Reuters")
            source_reliability = st.slider("Source Reliability", min_value=0.0, max_value=1.0, value=0.85, step=0.05)
        with col_c2:
            verifiable = st.selectbox("Verifiability Status", ["VERIFIABLE", "UNVERIFIABLE"])
            label = st.selectbox("Claim Stance Label", ["SUPPORTS", "REFUTES"])

        submit_custom = st.form_submit_button("Submit & Run Workflow")

        if submit_custom:
            if not claim_text.strip():
                st.error("Please enter some claim text.")
            else:
                with st.spinner("Running Multi-Agent Trust Evaluation Pipeline..."):
                    # Prepare mock triples since LLM extracts them, but Pydantic requires fields
                    custom_claim = {
                        "id": f"CUST-{str(uuid.uuid4())[:8]}",
                        "timestamp": None,
                        "source_id": source_id,
                        "source_reliability": source_reliability,
                        "verifiable": verifiable,
                        "label": label,
                        "claim": claim_text,
                        "subject": "",
                        "predicate": "",
                        "object": ""
                    }
                    
                    try:
                        res = requests.post(f"{API_URL}/claims", json=custom_claim)
                        if res.status_code == 200:
                            res_data = res.json()
                            action = res_data.get("action", "UNKNOWN")
                            st.success(f"Claim successfully processed! Action: **{action}**")
                            
                            # Fetch last change log to show explanation
                            time.sleep(0.5)
                            changelog_res = requests.get(f"{API_URL}/changelog?limit=1")
                            if changelog_res.status_code == 200 and changelog_res.json():
                                last_log = changelog_res.json()[0]
                                st.markdown("### 🔍 System Audit Details")
                                st.markdown(f"**Curator Action:** `{action}`")
                                st.markdown(f"**Reasoning / Explanation:** {last_log.get('reason')}")
                                st.markdown(f"**Confidence Delta:** `{last_log.get('confidence_delta', 0.0):+.3f}`")
                        else:
                            st.error(f"Error {res.status_code}: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
