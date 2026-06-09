import streamlit as st
import requests
import plotly.graph_objects as go

API_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

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
    --accent-cyan: #00cec9;
    --accent-orange: #e17055;
    --accent-red: #d63031;
    --accent-blue: #0984e3;
    --accent-pink: #e84393;
}
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
}
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
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetricValue"] {
    font-weight: 800 !important;
    font-size: 2.2rem !important;
}
.page-header {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C5CE7, #a29bfe);
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
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 1.5rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.stat-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0.35rem 0.9rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid;
}
.badge-accepted { background: rgba(0,184,148,0.1); color: #00b894; border-color: rgba(0,184,148,0.3); }
.badge-updated { background: rgba(9,132,227,0.1); color: #74b9ff; border-color: rgba(9,132,227,0.3); }
.badge-rejected { background: rgba(214,48,49,0.1); color: #ff7675; border-color: rgba(214,48,49,0.3); }
.badge-downgraded { background: rgba(225,112,85,0.1); color: #e17055; border-color: rgba(225,112,85,0.3); }
.badge-forgotten { background: rgba(99,110,114,0.1); color: #b2bec3; border-color: rgba(99,110,114,0.3); }
.badge-merged { background: rgba(108,92,231,0.1); color: #a29bfe; border-color: rgba(108,92,231,0.3); }
.action-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem;
    margin-top: 1rem;
}
.action-card {
    background: var(--bg-card);
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
}
.action-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}
.action-count {
    font-size: 2rem;
    font-weight: 800;
}
.action-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
}
.stButton > button {
    background: linear-gradient(135deg, #6C5CE7, #a29bfe) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(108,92,231,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(108,92,231,0.45) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────
st.markdown('<div class="page-header">📊 System Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Real-time overview of the memory intelligence pipeline</div>', unsafe_allow_html=True)

try:
    response = requests.get(f"{API_URL}/dashboard")
    if response.status_code == 200:
        stats = response.json()
        
        # ── Top Metrics Row ─────────────────────────────────────────────
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Claims Processed", stats.get("total_claims", 0))
        col2.metric("Total Memories", stats.get("total_memories", 0))
        col3.metric("Active Memories", stats.get("active_memories", 0))
        col4.metric("Forgotten Memories", stats.get("forgotten_memories", 0))
        
        st.markdown("---")
        
        # ── Action Breakdown ────────────────────────────────────────────
        left_col, right_col = st.columns([1.2, 1])
        
        with left_col:
            st.markdown('<div class="section-title">⚡ Action Breakdown</div>', unsafe_allow_html=True)
            
            accepted = stats.get("accepted_count", 0)
            updated = stats.get("updated_count", 0)
            rejected = stats.get("rejected_count", 0)
            downgraded = stats.get("downgraded_count", 0)
            forgotten = stats.get("forgotten_count", 0)
            merged = stats.get("merged_count", 0)
            
            st.markdown(f"""
            <div class="action-grid">
                <div class="action-card">
                    <div class="action-count" style="color: #00b894;">{accepted}</div>
                    <div class="action-label" style="color: #00b894;">Accepted</div>
                </div>
                <div class="action-card">
                    <div class="action-count" style="color: #74b9ff;">{updated}</div>
                    <div class="action-label" style="color: #74b9ff;">Updated</div>
                </div>
                <div class="action-card">
                    <div class="action-count" style="color: #ff7675;">{rejected}</div>
                    <div class="action-label" style="color: #ff7675;">Rejected</div>
                </div>
                <div class="action-card">
                    <div class="action-count" style="color: #e17055;">{downgraded}</div>
                    <div class="action-label" style="color: #e17055;">Downgraded</div>
                </div>
                <div class="action-card">
                    <div class="action-count" style="color: #b2bec3;">{forgotten}</div>
                    <div class="action-label" style="color: #b2bec3;">Forgotten</div>
                </div>
                <div class="action-card">
                    <div class="action-count" style="color: #a29bfe;">{merged}</div>
                    <div class="action-label" style="color: #a29bfe;">Merged</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with right_col:
            st.markdown('<div class="section-title">📈 Action Distribution</div>', unsafe_allow_html=True)
            
            labels = []
            values = []
            colors = []
            action_map = [
                ("Accepted", accepted, "#00b894"),
                ("Updated", updated, "#0984e3"),
                ("Rejected", rejected, "#d63031"),
                ("Downgraded", downgraded, "#e17055"),
                ("Forgotten", forgotten, "#636e72"),
                ("Merged", merged, "#6C5CE7"),
            ]
            for label, val, color in action_map:
                if val > 0:
                    labels.append(label)
                    values.append(val)
                    colors.append(color)
            
            if values:
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.55,
                    marker=dict(colors=colors, line=dict(color='#0a0a14', width=2)),
                    textfont=dict(size=12, color="white", family="Inter"),
                    hoverinfo="label+value+percent",
                )])
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e8e8f0", family="Inter"),
                    showlegend=True,
                    legend=dict(
                        font=dict(size=11, color="#9090b0"),
                        bgcolor="rgba(0,0,0,0)",
                    ),
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=300,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No actions recorded yet.")
        
        st.markdown("---")
        
        # ── Memory Status Summary ───────────────────────────────────────
        st.markdown('<div class="section-title">🧠 Memory Status Summary</div>', unsafe_allow_html=True)
        
        active = stats.get("active_memories", 0)
        low_conf = stats.get("low_confidence_memories", 0)
        forgotten_mem = stats.get("forgotten_memories", 0)
        total = stats.get("total_memories", 0)
        
        if total > 0:
            active_pct = int(active / total * 100) if total else 0
            st.markdown(f"""
            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                <span class="stat-badge badge-accepted">🟢 Active: {active} ({active_pct}%)</span>
                <span class="stat-badge badge-downgraded">🟡 Low Confidence: {low_conf}</span>
                <span class="stat-badge badge-forgotten">⚫ Forgotten: {forgotten_mem}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar
            st.markdown(f"""
            <div style="margin-top: 1rem; background: rgba(22,22,40,0.7); border-radius: 8px; overflow: hidden; height: 8px;">
                <div style="height: 100%; width: {active_pct}%; background: linear-gradient(90deg, #00b894, #55efc4); border-radius: 8px; transition: width 0.5s ease;"></div>
            </div>
            <div style="color: #9090b0; font-size: 0.75rem; margin-top: 0.3rem;">{active_pct}% of memories are actively trusted</div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn, _ = st.columns([1, 5])
        with col_btn:
            if st.button("🔄 Refresh Dashboard"):
                st.rerun()
            
    else:
        st.error(f"Failed to load dashboard stats: {response.text}")
except Exception as e:
    st.error(f"Could not connect to backend API: {e}")
