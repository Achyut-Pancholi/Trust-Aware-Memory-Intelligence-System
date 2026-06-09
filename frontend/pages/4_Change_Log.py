import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="Change Log", page_icon="📜", layout="wide")

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
.section-title {
    font-size: 1.1rem; font-weight: 700; color: #e8e8f0;
    margin: 1.5rem 0 1rem; display: flex; align-items: center; gap: 8px;
}
.log-row {
    display: grid;
    grid-template-columns: 160px 100px 1fr 80px;
    gap: 1rem;
    padding: 0.9rem 1.2rem;
    border-bottom: 1px solid rgba(108,92,231,0.08);
    align-items: center;
    transition: background 0.2s ease;
}
.log-row:hover {
    background: rgba(108,92,231,0.05);
}
.log-header {
    display: grid;
    grid-template-columns: 160px 100px 1fr 80px;
    gap: 1rem;
    padding: 0.7rem 1.2rem;
    border-bottom: 2px solid rgba(108,92,231,0.2);
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #9090b0;
}
.log-time { color: #9090b0; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; }
.log-action {
    display: inline-block;
    padding: 0.2rem 0.55rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    text-align: center;
}
.log-reason { color: #b2bec3; font-size: 0.82rem; line-height: 1.5; }
.log-delta { font-weight: 700; font-size: 0.85rem; text-align: center; }
details.expand-reason {
    margin-top: 0.2rem;
}
details.expand-reason summary {
    color: #a29bfe; font-size: 0.75rem; cursor: pointer;
    font-weight: 600; list-style: none; display: inline-flex; align-items: center; gap: 4px;
}
details.expand-reason summary::-webkit-details-marker { display: none; }
details.expand-reason summary::before { content: '\25b6 '; font-size: 0.6rem; }
details.expand-reason[open] summary::before { content: '\25bc '; }
details.expand-reason .full-text {
    color: #b2bec3; font-size: 0.82rem; line-height: 1.6;
    margin-top: 0.3rem; padding: 0.5rem 0.7rem;
    background: rgba(108,92,231,0.05); border-radius: 8px;
    border-left: 2px solid rgba(108,92,231,0.3);
}
.filter-chips {
    display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;
}
.filter-chip {
    padding: 0.3rem 0.8rem; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600;
    cursor: pointer; transition: all 0.2s ease;
    border: 1px solid;
}
.summary-row {
    display: flex; gap: 0.8rem; margin-bottom: 1.2rem; flex-wrap: wrap;
}
.summary-item {
    background: var(--bg-card);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 0.6rem 1rem;
    font-size: 0.82rem;
    color: #9090b0;
}
.summary-item strong { font-size: 1.1rem; }
.stSelectbox > div > div {
    background: rgba(22,22,40,0.7) !important;
    border: 1px solid rgba(108,92,231,0.15) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

ACTION_COLORS = {
    "ACCEPTED":   {"color": "#00b894", "bg": "rgba(0,184,148,0.15)"},
    "UPDATED":    {"color": "#0984e3", "bg": "rgba(9,132,227,0.15)"},
    "REJECTED":   {"color": "#d63031", "bg": "rgba(214,48,49,0.15)"},
    "DOWNGRADED": {"color": "#e17055", "bg": "rgba(225,112,85,0.15)"},
    "FORGOTTEN":  {"color": "#636e72", "bg": "rgba(99,110,114,0.15)"},
    "MERGED":     {"color": "#6C5CE7", "bg": "rgba(108,92,231,0.15)"},
}

# ── Header ──────────────────────────────────────────────────────────────
st.markdown('<div class="page-header">📜 System Change Log</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Immutable audit trail of every decision the memory curator made</div>', unsafe_allow_html=True)

try:
    response = requests.get(f"{API_URL}/changelog?limit=500")
    if response.status_code == 200:
        logs = response.json()
        if not logs:
            st.info("No logs available. Run the demo to generate data.")
        else:
            # ── Summary ─────────────────────────────────────────────────
            action_counts = {}
            for l in logs:
                a = l.get("action", "?")
                action_counts[a] = action_counts.get(a, 0) + 1
            
            summary_html = '<div class="summary-row">'
            summary_html += f'<div class="summary-item">📋 Total Entries: <strong style="color: #a29bfe;">{len(logs)}</strong></div>'
            for action, count in sorted(action_counts.items()):
                ac = ACTION_COLORS.get(action, {"color": "#9090b0"})
                summary_html += f'<div class="summary-item">{action}: <strong style="color: {ac["color"]};">{count}</strong></div>'
            summary_html += '</div>'
            st.markdown(summary_html, unsafe_allow_html=True)
            
            # ── Filter ──────────────────────────────────────────────────
            filter_col1, filter_col2 = st.columns([1, 3])
            with filter_col1:
                action_filter = st.selectbox("Filter by Action", ["ALL"] + list(action_counts.keys()))
            
            filtered_logs = [l for l in logs if action_filter == "ALL" or l.get("action") == action_filter]
            
            # ── Table Header ────────────────────────────────────────────
            st.markdown("""
            <div style="background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: 16px; overflow: hidden;">
                <div class="log-header">
                    <span>Timestamp</span>
                    <span>Action</span>
                    <span>Reason</span>
                    <span>Δ Conf</span>
                </div>
            """, unsafe_allow_html=True)
            
            # ── Log Rows ────────────────────────────────────────────────
            rows_html = ""
            for log in filtered_logs:
                action = log.get("action", "?")
                ac = ACTION_COLORS.get(action, {"color": "#9090b0", "bg": "rgba(144,144,176,0.1)"})
                delta = log.get("confidence_delta", 0)
                delta_str = f"+{delta:.3f}" if delta > 0 else f"{delta:.3f}" if delta < 0 else "0.000"
                delta_color = "#00b894" if delta > 0 else "#d63031" if delta < 0 else "#636e72"
                
                reason = log.get("reason", "")
                short_reason = reason[:100] if len(reason) > 100 else reason
                needs_expand = len(reason) > 100
                
                expand_html = ""
                if needs_expand:
                    expand_html = f'<details class="expand-reason"><summary>View full</summary><div class="full-text">{reason}</div></details>'
                
                rows_html += f"""
                <div class="log-row">
                    <span class="log-time">{log.get("timestamp", "")[:19]}</span>
                    <span class="log-action" style="background: {ac['bg']}; color: {ac['color']};">{action}</span>
                    <span class="log-reason">{short_reason}{"..." if needs_expand else ""}{expand_html}</span>
                    <span class="log-delta" style="color: {delta_color};">{delta_str}</span>
                </div>
                """
            
            rows_html += "</div>"
            st.markdown(rows_html, unsafe_allow_html=True)
            
    else:
        st.error("Failed to fetch changelogs.")
except Exception as e:
    st.error(f"Could not connect to backend API: {e}")
