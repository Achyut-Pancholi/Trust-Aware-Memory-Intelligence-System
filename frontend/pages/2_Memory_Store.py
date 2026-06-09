import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from frontend.startup import ensure_backend_running
ensure_backend_running()

import streamlit as st
import requests
import pandas as pd

import os
API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(page_title="Memory Store", page_icon="🗄️", layout="wide")

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

.memory-card {
    background: var(--bg-card);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 0.8rem;
    backdrop-filter: blur(12px);
    transition: all 0.3s ease;
}
.memory-card:hover {
    border-color: #6C5CE7;
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(108,92,231,0.12);
}
.memory-subject {
    font-size: 1.15rem; font-weight: 700; color: #e8e8f0;
    margin-bottom: 0.2rem;
}
.memory-triple {
    color: #a29bfe; font-size: 0.9rem; font-weight: 500;
    margin-bottom: 0.7rem;
}
.memory-meta {
    display: flex; gap: 1rem; flex-wrap: wrap; align-items: center;
}
.meta-chip {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 0.25rem 0.7rem; border-radius: 20px;
    font-size: 0.72rem; font-weight: 600;
    border: 1px solid;
}
.status-active { background: rgba(0,184,148,0.1); color: #00b894; border-color: rgba(0,184,148,0.3); }
.status-low_confidence { background: rgba(225,112,85,0.1); color: #e17055; border-color: rgba(225,112,85,0.3); }
.status-forgotten { background: rgba(99,110,114,0.15); color: #b2bec3; border-color: rgba(99,110,114,0.3); }
.status-outdated { background: rgba(253,203,110,0.1); color: #fdcb6e; border-color: rgba(253,203,110,0.3); }
.status-rejected { background: rgba(214,48,49,0.1); color: #ff7675; border-color: rgba(214,48,49,0.3); }

.confidence-bar-bg {
    width: 120px; height: 6px; background: rgba(255,255,255,0.08);
    border-radius: 3px; overflow: hidden; display: inline-block; vertical-align: middle; margin-left: 6px;
}
.confidence-bar-fill {
    height: 100%; border-radius: 3px;
    transition: width 0.5s ease;
}

.filter-row {
    display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.2rem;
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
    box-shadow: 0 4px 15px rgba(108,92,231,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────
st.markdown('<div class="page-header">🗄️ Memory Store</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Browse all stored beliefs with confidence scores, sources, and status</div>', unsafe_allow_html=True)

try:
    response = requests.get(f"{API_URL}/memory?limit=100")
    if response.status_code == 200:
        memories = response.json()
        
        if not memories:
            st.info("No memories found. Run the demo to populate the memory store.")
        else:
            # ── Filters ─────────────────────────────────────────────────
            filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])
            with filter_col1:
                status_filter = st.selectbox("Filter by Status", ["ALL", "ACTIVE", "LOW_CONFIDENCE", "OUTDATED", "FORGOTTEN", "REJECTED"])
            with filter_col2:
                sort_by = st.selectbox("Sort by", ["Confidence (High→Low)", "Confidence (Low→High)", "Recently Updated", "Subject A-Z"])
            
            filtered = [m for m in memories if status_filter == "ALL" or m["status"] == status_filter]
            
            # Sort
            if sort_by == "Confidence (High→Low)":
                filtered.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            elif sort_by == "Confidence (Low→High)":
                filtered.sort(key=lambda x: x.get("confidence", 0))
            elif sort_by == "Recently Updated":
                filtered.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
            elif sort_by == "Subject A-Z":
                filtered.sort(key=lambda x: x.get("subject", ""))
            
            # Count display
            st.markdown(f"""
            <div style="color: #9090b0; font-size: 0.85rem; margin-bottom: 1rem;">
                Showing <strong style="color: #a29bfe;">{len(filtered)}</strong> of {len(memories)} memories
            </div>
            """, unsafe_allow_html=True)
            
            # ── Memory Cards ────────────────────────────────────────────
            for mem in filtered:
                status = mem.get("status", "ACTIVE").lower()
                confidence = mem.get("confidence", 0)
                conf_pct = int(confidence * 100)
                
                # Color based on confidence
                if confidence >= 0.7:
                    bar_color = "#00b894"
                elif confidence >= 0.4:
                    bar_color = "#fdcb6e"
                else:
                    bar_color = "#d63031"
                
                sources_list = mem.get("sources", [])
                source_names = ", ".join([s.get("source_id", "?") for s in sources_list]) if sources_list else "Unknown"
                
                st.markdown(f"""
                <div class="memory-card">
                    <div class="memory-subject">{mem.get("subject", "—")}</div>
                    <div class="memory-triple">
                        {mem.get("predicate", "—")} → <strong>{mem.get("object", "—")}</strong>
                    </div>
                    <div class="memory-meta">
                        <span class="meta-chip status-{status}">
                            {"🟢" if status == "active" else "🟡" if status == "low_confidence" else "⚫" if status == "forgotten" else "🔴" if status == "rejected" else "🟠"}
                            {mem.get("status", "—")}
                        </span>
                        <span style="color: #9090b0; font-size: 0.8rem;">
                            Confidence: <strong style="color: {bar_color};">{conf_pct}%</strong>
                            <span class="confidence-bar-bg">
                                <span class="confidence-bar-fill" style="width: {conf_pct}%; background: {bar_color};"></span>
                            </span>
                        </span>
                        <span style="color: #9090b0; font-size: 0.8rem;">
                            📚 Sources: <strong style="color: #dfe6e9;">{source_names}</strong>
                        </span>
                        <span style="color: #9090b0; font-size: 0.8rem;">
                            🔁 Corroborations: <strong style="color: #dfe6e9;">{mem.get("corroboration_count", 1)}</strong>
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
    else:
        st.error("Failed to fetch memories.")
except Exception as e:
    st.error(f"Could not connect to backend API: {e}")
