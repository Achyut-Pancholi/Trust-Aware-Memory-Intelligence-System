import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

import os
API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(page_title="Evolution Timeline", page_icon="📈", layout="wide")

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
.action-timeline-card {
    background: var(--bg-card);
    border-left: 3px solid;
    border-radius: 0 14px 14px 0;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.6rem;
    transition: all 0.3s ease;
}
.action-timeline-card:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.atc-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 0.4rem;
}
.atc-action {
    font-weight: 700; font-size: 0.85rem;
    padding: 0.2rem 0.6rem; border-radius: 6px;
}
.atc-time { color: #9090b0; font-size: 0.78rem; }
.atc-reason { color: #b2bec3; font-size: 0.85rem; line-height: 1.5; }
.atc-delta {
    font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem;
}
details.expand-reason {
    margin-top: 0.3rem;
}
details.expand-reason summary {
    color: #a29bfe; font-size: 0.78rem; cursor: pointer;
    font-weight: 600; list-style: none; display: inline-flex; align-items: center; gap: 4px;
}
details.expand-reason summary::-webkit-details-marker { display: none; }
details.expand-reason summary::before { content: '▶ '; font-size: 0.65rem; }
details.expand-reason[open] summary::before { content: '▼ '; }
details.expand-reason .full-text {
    color: #b2bec3; font-size: 0.85rem; line-height: 1.6;
    margin-top: 0.4rem; padding: 0.6rem 0.8rem;
    background: rgba(108,92,231,0.05); border-radius: 8px;
    border-left: 2px solid rgba(108,92,231,0.3);
}
.stSelectbox > div > div {
    background: rgba(22,22,40,0.7) !important;
    border: 1px solid rgba(108,92,231,0.15) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

ACTION_STYLES = {
    "ACCEPTED":   {"color": "#00b894", "bg": "rgba(0,184,148,0.12)", "icon": "✅"},
    "UPDATED":    {"color": "#0984e3", "bg": "rgba(9,132,227,0.12)", "icon": "🔄"},
    "REJECTED":   {"color": "#d63031", "bg": "rgba(214,48,49,0.12)", "icon": "❌"},
    "DOWNGRADED": {"color": "#e17055", "bg": "rgba(225,112,85,0.12)", "icon": "⬇️"},
    "FORGOTTEN":  {"color": "#636e72", "bg": "rgba(99,110,114,0.15)", "icon": "💨"},
    "MERGED":     {"color": "#6C5CE7", "bg": "rgba(108,92,231,0.12)", "icon": "🔗"},
}

# ── Header ──────────────────────────────────────────────────────────────
st.markdown('<div class="page-header">📈 Memory Evolution Timeline</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Visualize how beliefs evolve as new evidence arrives</div>', unsafe_allow_html=True)

try:
    response = requests.get(f"{API_URL}/changelog?limit=200")
    if response.status_code == 200:
        logs = response.json()
        
        if logs:
            # ── Build per-memory confidence chart ───────────────────────
            mem_response = requests.get(f"{API_URL}/memory?limit=200")
            memories = mem_response.json() if mem_response.status_code == 200 else []
            
            if memories:
                # Memory selector
                memory_options = {f"{m['subject']} → {m['predicate']} → {m['object']}": m['id'] for m in memories}
                selected = st.selectbox("🔎 Select a Memory to Track", list(memory_options.keys()))
                selected_id = memory_options[selected]
                
                # Filter logs for this memory
                mem_logs = [l for l in logs if l.get("memory_id") == selected_id]
                mem_logs.sort(key=lambda x: x.get("timestamp", ""))
                
                if mem_logs:
                    # Build cumulative confidence
                    timestamps = []
                    confidences = []
                    actions = []
                    running_conf = 0
                    
                    for log in mem_logs:
                        timestamps.append(log["timestamp"][:19])
                        delta = log.get("confidence_delta", 0)
                        nv = log.get("new_value")
                        if nv and isinstance(nv, dict) and "confidence" in nv:
                            running_conf = nv["confidence"]
                        else:
                            running_conf = max(0, min(1, running_conf + delta))
                        confidences.append(round(running_conf, 3))
                        actions.append(log.get("action", "?"))
                    
                    fig = go.Figure()
                    
                    # Area fill
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=confidences,
                        fill='tozeroy',
                        fillcolor='rgba(108,92,231,0.08)',
                        line=dict(color='#6C5CE7', width=3, shape='spline'),
                        mode='lines+markers',
                        marker=dict(size=10, color='#6C5CE7', line=dict(width=2, color='#0a0a14')),
                        text=[f"Action: {a}<br>Confidence: {c}" for a, c in zip(actions, confidences)],
                        hoverinfo='text+x',
                        name='Confidence'
                    ))
                    
                    # Action color markers
                    for i, (t, c, a) in enumerate(zip(timestamps, confidences, actions)):
                        style = ACTION_STYLES.get(a, {"color": "#9090b0"})
                        fig.add_trace(go.Scatter(
                            x=[t], y=[c],
                            mode='markers+text',
                            marker=dict(size=14, color=style["color"], line=dict(width=2, color='#0a0a14')),
                            text=[a],
                            textposition='top center',
                            textfont=dict(size=9, color=style["color"], family="Inter"),
                            showlegend=False,
                            hoverinfo='skip',
                        ))
                    
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#e8e8f0', family='Inter'),
                        xaxis=dict(
                            showgrid=False,
                            title=dict(text="Time", font=dict(color='#9090b0', size=12)),
                            tickfont=dict(color='#9090b0', size=10),
                            linecolor='rgba(108,92,231,0.2)',
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(108,92,231,0.08)',
                            title=dict(text="Confidence", font=dict(color='#9090b0', size=12)),
                            tickfont=dict(color='#9090b0', size=10),
                            range=[0, 1.05],
                            linecolor='rgba(108,92,231,0.2)',
                        ),
                        margin=dict(t=30, b=50, l=60, r=20),
                        height=380,
                        showlegend=False,
                        hovermode='x unified',
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No history found for this memory.")
            
            st.markdown("---")
            
            # ── Action Timeline ─────────────────────────────────────────
            st.markdown('<div class="section-title">🕐 Recent Actions Timeline</div>', unsafe_allow_html=True)
            
            for log in logs[:15]:
                action = log.get("action", "ACCEPTED")
                style = ACTION_STYLES.get(action, {"color": "#9090b0", "bg": "rgba(144,144,176,0.1)", "icon": "•"})
                delta = log.get("confidence_delta", 0)
                delta_str = f"+{delta:.3f}" if delta > 0 else f"{delta:.3f}" if delta < 0 else "0.000"
                delta_color = "#00b894" if delta > 0 else "#d63031" if delta < 0 else "#636e72"
                
                reason = log.get("reason", "")
                short_reason = reason[:120] if len(reason) > 120 else reason
                needs_expand = len(reason) > 120
                
                expand_html = ""
                if needs_expand:
                    expand_html = f'<details class="expand-reason"><summary>View full reason</summary><div class="full-text">{reason}</div></details>'
                else:
                    # Keep it empty without introducing blank lines in the HTML string
                    expand_html = ""
                
                html_content = (
                    f'<div class="action-timeline-card" style="border-left-color: {style["color"]};">'
                    f'    <div class="atc-header">'
                    f'        <span class="atc-action" style="background: {style["bg"]}; color: {style["color"]};">'
                    f'            {style["icon"]} {action}'
                    f'        </span>'
                    f'        <span class="atc-time">{log.get("timestamp", "")[:19]}</span>'
                    f'    </div>'
                    f'    <div class="atc-reason">{short_reason}{"..." if needs_expand else ""}</div>'
                    f'    {expand_html}'
                    f'    <div class="atc-delta" style="color: {delta_color};">'
                    f'        Δ Confidence: {delta_str} &nbsp;|&nbsp; Claim: {log.get("claim_id", "—")}'
                    f'    </div>'
                    f'</div>'
                )
                st.markdown(html_content, unsafe_allow_html=True)
        else:
            st.info("No evolution history found. Run the demo to generate data.")
    else:
        st.error("Failed to fetch history.")
except Exception as e:
    st.error(f"Could not connect to backend API: {e}")
