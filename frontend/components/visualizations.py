import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pyvis.network import Network
import tempfile

def create_confidence_trend_chart(changelogs: list):
    if not changelogs:
        return None
    
    df = pd.DataFrame([{"timestamp": log["timestamp"], "confidence_delta": log["confidence_delta"]} for log in changelogs])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values("timestamp")
    df['cumulative_confidence'] = df['confidence_delta'].cumsum() # Simplified for viz
    
    fig = px.line(df, x="timestamp", y="cumulative_confidence", title="Confidence Evolution Timeline")
    return fig

def create_knowledge_graph(memories: list):
    net = Network(height='600px', width='100%', directed=True, notebook=False)
    
    for mem in memories:
        if mem["status"] == "ACTIVE":
            sub = mem["subject"]
            obj = mem["object"]
            pred = mem["predicate"]
            
            net.add_node(sub, label=sub, title=sub, color="#97C2FC")
            net.add_node(obj, label=obj, title=obj, color="#FF9999")
            net.add_edge(sub, obj, label=pred, title=f"Confidence: {mem['confidence']:.2f}")
            
    # Generate HTML
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        net.save_graph(tmp.name)
        with open(tmp.name, 'r', encoding='utf-8') as f:
            html = f.read()
    return html

def create_provenance_graph(timeline: list):
    net = Network(height='400px', width='100%', directed=True, notebook=False)
    
    prev_node = "START"
    net.add_node(prev_node, label="Start", color="green")
    
    for i, log in enumerate(timeline):
        node_id = f"log_{i}"
        label = f"{log['action']}\n{log['timestamp'][:10]}"
        net.add_node(node_id, label=label, title=log['reason'], color="orange" if "UPDATE" in log['action'] else "blue")
        net.add_edge(prev_node, node_id)
        prev_node = node_id
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        net.save_graph(tmp.name)
        with open(tmp.name, 'r', encoding='utf-8') as f:
            html = f.read()
    return html
