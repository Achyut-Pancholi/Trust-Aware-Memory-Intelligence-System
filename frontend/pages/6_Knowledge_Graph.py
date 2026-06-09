import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import requests
import streamlit.components.v1 as components

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Knowledge Graph", page_icon="🕸️", layout="wide")

# ── Page CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif !important; }
.page-header {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, #6C5CE7, #a29bfe);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin-bottom: 0.3rem;
}
.page-subtitle { color: #9090b0; font-size: 0.95rem; margin-bottom: 1.5rem; }
.graph-container {
    background: rgba(22,22,40,0.7);
    border: 1px solid rgba(108,92,231,0.15);
    border-radius: 16px;
    overflow: hidden;
    padding: 0;
}
.legend-row {
    display: flex; gap: 1.2rem; margin-bottom: 1rem; flex-wrap: wrap;
}
.legend-item {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.8rem; color: #9090b0;
}
.legend-dot {
    width: 12px; height: 12px; border-radius: 50%;
}
.stSelectbox > div > div {
    background: rgba(22,22,40,0.7) !important;
    border: 1px solid rgba(108,92,231,0.15) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────
st.markdown('<div class="page-header">🕸️ Knowledge Graph</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Interactive entity-relationship network of all active memories</div>', unsafe_allow_html=True)

# Legend
st.markdown("""
<div class="legend-row">
    <div class="legend-item"><div class="legend-dot" style="background: #6C5CE7;"></div> Subject Entities</div>
    <div class="legend-item"><div class="legend-dot" style="background: #00cec9;"></div> Object Values</div>
    <div class="legend-item"><div class="legend-dot" style="background: rgba(108,92,231,0.4);"></div> Edges = Predicates</div>
</div>
""", unsafe_allow_html=True)

try:
    response = requests.get(f"{API_URL}/memory?limit=200")
    if response.status_code == 200:
        memories = response.json()
        if not memories:
            st.info("No memories available. Run the demo to populate the graph.")
        else:
            # Filter option
            status_filter = st.selectbox("Filter Nodes by Status", ["ACTIVE", "ALL", "LOW_CONFIDENCE", "FORGOTTEN"])
            
            filtered = [m for m in memories if status_filter == "ALL" or m.get("status") == status_filter]
            
            if not filtered:
                st.info(f"No memories with status '{status_filter}' found.")
            else:
                # Build graph HTML directly (avoiding pyvis temp file issues)
                nodes_js = []
                edges_js = []
                seen_nodes = set()
                
                for mem in filtered:
                    sub = mem["subject"]
                    obj = mem["object"]
                    pred = mem["predicate"]
                    conf = mem.get("confidence", 0)
                    status = mem.get("status", "ACTIVE")
                    
                    if sub not in seen_nodes:
                        nodes_js.append(f'{{id: "{sub}", label: "{sub}", color: {{background: "#6C5CE7", border: "#a29bfe", highlight: {{background: "#a29bfe", border: "#6C5CE7"}}}}, font: {{color: "#e8e8f0", size: 14, face: "Inter"}}, shape: "dot", size: 25, borderWidth: 2}}')
                        seen_nodes.add(sub)
                    
                    obj_id = f"{sub}_{pred}_{obj}"
                    if obj_id not in seen_nodes:
                        # Color based on status
                        if status == "ACTIVE":
                            obj_color = "#00cec9"
                            obj_border = "#00b894"
                        elif status == "LOW_CONFIDENCE":
                            obj_color = "#e17055"
                            obj_border = "#d63031"
                        else:
                            obj_color = "#636e72"
                            obj_border = "#2d3436"
                        
                        nodes_js.append(f'{{id: "{obj_id}", label: "{obj}", color: {{background: "{obj_color}", border: "{obj_border}", highlight: {{background: "{obj_border}", border: "{obj_color}"}}}}, font: {{color: "#e8e8f0", size: 12, face: "Inter"}}, shape: "dot", size: 18, borderWidth: 2}}')
                        seen_nodes.add(obj_id)
                    
                    edge_label = f"{pred} ({conf:.0%})"
                    edges_js.append(f'{{from: "{sub}", to: "{obj_id}", label: "{edge_label}", color: {{color: "rgba(108,92,231,0.5)", highlight: "#a29bfe", hover: "#a29bfe"}}, font: {{color: "#9090b0", size: 10, face: "Inter", strokeWidth: 0}}, arrows: "to", width: {max(1, int(conf * 4))}, smooth: {{type: "curvedCW", roundness: 0.15}}}}')
                
                nodes_str = ",\n".join(nodes_js)
                edges_str = ",\n".join(edges_js)
                
                graph_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.6/dist/vis-network.min.js"></script>
                    <style>
                        body {{ margin: 0; padding: 0; background: #0a0a14; overflow: hidden; }}
                        #graph {{ width: 100%; height: 600px; }}
                    </style>
                </head>
                <body>
                    <div id="graph"></div>
                    <script>
                        var nodes = new vis.DataSet([{nodes_str}]);
                        var edges = new vis.DataSet([{edges_str}]);
                        var container = document.getElementById('graph');
                        var data = {{ nodes: nodes, edges: edges }};
                        var options = {{
                            physics: {{
                                enabled: true,
                                barnesHut: {{
                                    gravitationalConstant: -3000,
                                    centralGravity: 0.2,
                                    springLength: 150,
                                    springConstant: 0.04,
                                    damping: 0.09
                                }},
                                stabilization: {{ iterations: 150 }}
                            }},
                            interaction: {{
                                hover: true,
                                dragView: true,
                                zoomView: true,
                                dragNodes: true,
                                tooltipDelay: 100
                            }},
                            layout: {{
                                improvedLayout: true
                            }}
                        }};
                        var network = new vis.Network(container, data, options);
                    </script>
                </body>
                </html>
                """
                
                st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                components.html(graph_html, height=620)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="color: #9090b0; font-size: 0.8rem; margin-top: 0.5rem;">
                    📊 Showing <strong style="color: #a29bfe;">{len(filtered)}</strong> memories as graph nodes &nbsp;|&nbsp; 
                    Drag nodes to rearrange &nbsp;|&nbsp; Scroll to zoom
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("Failed to fetch memories.")
except Exception as e:
    st.error(f"Could not connect to backend API: {e}")
