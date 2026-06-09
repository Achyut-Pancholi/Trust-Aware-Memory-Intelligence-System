import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import requests
import streamlit.components.v1 as components
from frontend.components.visualizations import create_provenance_graph

API_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="Explainability", page_icon="🔍", layout="wide")

# ── Page CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root {
    --bg-card: rgba(22, 22, 40, 0.7);
    --glass-border: rgba(108, 92, 231, 0.15);
    --text-primary: #e8e8f0;
    --text-secondary: #9090b0;
}
html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif !important; }
.page-header {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, #6C5CE7, #a29bfe);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin-bottom: 0.3rem;
}
.page-subtitle { color: #9090b0; font-size: 0.95rem; margin-bottom: 1.5rem; }

.belief-card {
    background: var(--bg-card);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(12px);
}
.belief-text {
    font-size: 1.3rem; font-weight: 700; color: #e8e8f0;
    margin-bottom: 0.8rem;
}
.confidence-display {
    display: flex; align-items: center; gap: 1rem;
}
.conf-value {
    font-size: 2.5rem; font-weight: 800;
    background: linear-gradient(135deg, #6C5CE7, #00cec9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.conf-bar-outer {
    flex: 1; height: 10px; background: rgba(255,255,255,0.06);
    border-radius: 5px; overflow: hidden;
}
.conf-bar-inner {
    height: 100%; border-radius: 5px;
    background: linear-gradient(90deg, #6C5CE7, #00cec9);
    transition: width 0.8s ease;
}

.reasoning-box {
    background: rgba(108,92,231,0.06);
    border: 1px solid rgba(108,92,231,0.15);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    color: #b2bec3;
    font-size: 0.92rem;
    line-height: 1.7;
    margin: 1rem 0;
}
.reasoning-box strong { color: #e8e8f0; }

.source-card {
    background: var(--bg-card);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
}
.source-name { font-weight: 700; color: #e8e8f0; font-size: 0.95rem; }
.source-reliability {
    font-size: 0.82rem; color: #9090b0; margin-top: 0.2rem;
}
.rel-bar {
    width: 80px; height: 5px; background: rgba(255,255,255,0.06);
    border-radius: 3px; overflow: hidden; display: inline-block; vertical-align: middle; margin-left: 8px;
}
.rel-bar-fill {
    height: 100%; border-radius: 3px;
}

.section-title {
    font-size: 1.05rem; font-weight: 700; color: #e8e8f0;
    margin: 1.2rem 0 0.8rem; display: flex; align-items: center; gap: 8px;
}
.stSelectbox > div > div {
    background: rgba(22,22,40,0.7) !important;
    border: 1px solid rgba(108,92,231,0.15) !important;
    border-radius: 10px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #6C5CE7, #a29bfe) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 600 !important;
    padding: 0.6rem 2rem !important;
    box-shadow: 0 4px 15px rgba(108,92,231,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(108,92,231,0.45) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────
st.markdown('<div class="page-header">🔍 Explainability Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Understand why the system believes a specific fact — with full reasoning and provenance</div>', unsafe_allow_html=True)

try:
    response = requests.get(f"{API_URL}/memory?limit=100")
    if response.status_code == 200:
        memories = response.json()
        if not memories:
            st.info("No memories available to explain. Run the demo first.")
        else:
            options = {f"{m['subject']}  →  {m['predicate']}  →  {m['object']}": m['id'] for m in memories}
            selected_option = st.selectbox("Select a Memory to Explain", list(options.keys()))
            
            if st.button("🧠 Generate AI Explanation"):
                memory_id = options[selected_option]
                with st.spinner("AI is analyzing provenance and generating explanation..."):
                    exp_response = requests.get(f"{API_URL}/memory/{memory_id}/explain")
                    
                    if exp_response.status_code == 200:
                        data = exp_response.json()
                        conf = data.get("current_confidence", 0)
                        conf_pct = int(conf * 100)
                        
                        # ── Belief Card ─────────────────────────────────
                        st.markdown(f"""
                        <div class="belief-card">
                            <div class="belief-text">📌 {data.get('claim_text', '—')}</div>
                            <div class="confidence-display">
                                <span class="conf-value">{conf_pct}%</span>
                                <div class="conf-bar-outer">
                                    <div class="conf-bar-inner" style="width: {conf_pct}%;"></div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # ── AI Reasoning ────────────────────────────────
                        st.markdown('<div class="section-title">🤖 AI Reasoning</div>', unsafe_allow_html=True)
                        reason_text = data.get("reason", "No reasoning available.")
                        st.markdown(f'<div class="reasoning-box">{reason_text}</div>', unsafe_allow_html=True)
                        
                        # ── Sources ─────────────────────────────────────
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown('<div class="section-title">✅ Supporting Sources</div>', unsafe_allow_html=True)
                            supporting = data.get("supporting_sources", [])
                            if supporting:
                                for src in supporting:
                                    rel = src.get("reliability", 0)
                                    rel_pct = int(rel * 100)
                                    bar_color = "#00b894" if rel >= 0.7 else "#fdcb6e" if rel >= 0.4 else "#d63031"
                                    st.markdown(f"""
                                    <div class="source-card">
                                        <div class="source-name">📰 {src.get("source_id", "Unknown")}</div>
                                        <div class="source-reliability">
                                            Reliability: <strong style="color: {bar_color};">{rel_pct}%</strong>
                                            <span class="rel-bar">
                                                <span class="rel-bar-fill" style="width: {rel_pct}%; background: {bar_color};"></span>
                                            </span>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="color: #636e72; font-size: 0.85rem;">No supporting sources found.</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown('<div class="section-title">❌ Contradicting Sources</div>', unsafe_allow_html=True)
                            contradicting = data.get("contradicting_sources", [])
                            if contradicting:
                                for src in contradicting:
                                    rel = src.get("reliability", 0)
                                    rel_pct = int(rel * 100)
                                    st.markdown(f"""
                                    <div class="source-card">
                                        <div class="source-name">⚠️ {src.get("source_id", "Unknown")}</div>
                                        <div class="source-reliability">
                                            Reliability: <strong style="color: #d63031;">{rel_pct}%</strong>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="color: #636e72; font-size: 0.85rem;">No contradicting sources found.</div>', unsafe_allow_html=True)
                        
                        # ── Provenance Graph ────────────────────────────
                        st.markdown("---")
                        st.markdown('<div class="section-title">🗺️ Provenance Timeline Graph</div>', unsafe_allow_html=True)
                        timeline = data.get("timeline", [])
                        if timeline:
                            html_graph = create_provenance_graph(timeline)
                            components.html(html_graph, height=450)
                        else:
                            st.info("No provenance timeline available.")
                    else:
                        st.error("Failed to generate explanation. Try again.")
except Exception as e:
    st.error(f"Could not connect to backend API: {e}")
