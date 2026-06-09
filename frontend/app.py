import subprocess
import sys
import time
import socket
import os

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

# Streamlit Cloud hack: Start the FastAPI backend automatically if it's not running
if not is_port_in_use(8000):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"], cwd=root_dir, stdout=sys.stdout, stderr=sys.stderr)
    time.sleep(4) # Give it a few seconds to boot up

import streamlit as st

st.set_page_config(
    page_title="Trust-Aware Memory Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ─── Root Variables ─── */
:root {
    --bg-primary: #0a0a14;
    --bg-secondary: #12121f;
    --bg-card: rgba(22, 22, 40, 0.7);
    --border-color: rgba(108, 92, 231, 0.2);
    --text-primary: #e8e8f0;
    --text-secondary: #9090b0;
    --accent-purple: #6C5CE7;
    --accent-blue: #0984e3;
    --accent-cyan: #00cec9;
    --accent-green: #00b894;
    --accent-orange: #e17055;
    --accent-red: #d63031;
    --accent-pink: #e84393;
    --gradient-1: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%);
    --gradient-2: linear-gradient(135deg, #0984e3 0%, #00cec9 100%);
    --gradient-3: linear-gradient(135deg, #00b894 0%, #55efc4 100%);
    --glass: rgba(22, 22, 40, 0.6);
    --glass-border: rgba(108, 92, 231, 0.15);
}

/* ─── Global Styles ─── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

[data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
}

[data-testid="stHeader"] {
    background: rgba(10, 10, 20, 0.8) !important;
    backdrop-filter: blur(20px) !important;
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #161630 100%) !important;
    border-right: 1px solid var(--glass-border) !important;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li {
    color: var(--text-secondary) !important;
    font-size: 0.9rem !important;
}

[data-testid="stSidebarNav"] a {
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.3s ease !important;
}

[data-testid="stSidebarNav"] a:hover {
    background: rgba(108, 92, 231, 0.15) !important;
}

[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: var(--gradient-1) !important;
    color: white !important;
    font-weight: 600 !important;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--accent-purple); border-radius: 3px; }

/* ─── Metric Cards ─── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.5rem !important;
    backdrop-filter: blur(12px) !important;
    transition: all 0.3s ease !important;
}
[data-testid="stMetric"]:hover {
    border-color: var(--accent-purple) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(108, 92, 231, 0.15) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 2rem !important;
}

/* ─── Buttons ─── */
.stButton > button {
    background: var(--gradient-1) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.8rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(108, 92, 231, 0.45) !important;
}

/* ─── DataFrames ─── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ─── Expanders ─── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

/* ─── Selectbox ─── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

/* ─── Spinner ─── */
.stSpinner > div > div {
    border-top-color: var(--accent-purple) !important;
}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: var(--text-secondary) !important;
    padding: 0.5rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--gradient-1) !important;
    color: white !important;
    border: none !important;
}

/* ─── Info/Success/Warning/Error boxes ─── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* ─── Hero Styles (Home Page Only) ─── */
.hero-container {
    text-align: center;
    padding: 3rem 2rem 2rem;
}
.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C5CE7, #a29bfe, #00cec9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1.15rem;
    color: var(--text-secondary);
    max-width: 600px;
    margin: 0 auto 2.5rem;
    line-height: 1.7;
}
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.2rem;
    max-width: 1100px;
    margin: 0 auto;
}
.feature-card {
    background: var(--bg-card);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.8rem 1.5rem;
    backdrop-filter: blur(12px);
    transition: all 0.35s ease;
    text-align: left;
}
.feature-card:hover {
    border-color: var(--accent-purple);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(108, 92, 231, 0.12);
}
.feature-icon {
    font-size: 2rem;
    margin-bottom: 0.8rem;
    display: block;
}
.feature-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.4rem;
}
.feature-desc {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

/* ─── Pulse animation for live indicator ─── */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
.live-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent-green);
    margin-right: 6px;
    animation: pulse 2s infinite;
}
</style>
""", unsafe_allow_html=True)

# ── Hero Section ────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🧠 Trust-Aware Memory Intelligence</div>
    <div class="hero-subtitle">
        A multi-agent system that ingests noisy, conflicting, and evolving claims —
        then transforms them into a curated, explainable knowledge store using trust-weighted reasoning.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Feature Cards ───────────────────────────────────────────────────────
st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <span class="feature-icon">📊</span>
        <div class="feature-title">Live Dashboard</div>
        <div class="feature-desc">Real-time metrics on claims processed, memory states, and action distribution across the system.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🗄️</span>
        <div class="feature-title">Memory Store</div>
        <div class="feature-desc">Browse all stored memories with confidence scores, source provenance, and status tracking.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">📈</span>
        <div class="feature-title">Evolution Timeline</div>
        <div class="feature-desc">Watch how beliefs evolve over time as new evidence arrives, with full state transition history.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">📜</span>
        <div class="feature-title">Immutable Change Log</div>
        <div class="feature-desc">Every decision is auditable. View the full provenance trail of accepts, updates, and rejections.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🔍</span>
        <div class="feature-title">Explainability Engine</div>
        <div class="feature-desc">Ask the AI why it believes a specific fact — it explains the reasoning, sources, and confidence history.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🕸️</span>
        <div class="feature-title">Knowledge Graph</div>
        <div class="feature-desc">Interactive 3D-style network diagram mapping subject → predicate → object relationships.</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0;">
        <span class="live-dot"></span>
        <span style="color: #00b894; font-weight: 600; font-size: 0.85rem;">System Online</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("##### Navigation")
    st.markdown("""
    Use the pages above to explore:
    - **Dashboard** — system overview
    - **Memory Store** — browse memories
    - **Timeline** — confidence evolution
    - **Change Log** — audit trail
    - **Explainability** — AI reasoning
    - **Knowledge Graph** — entity map
    - **Testing Playground** — run live testing & reset DB
    """)
