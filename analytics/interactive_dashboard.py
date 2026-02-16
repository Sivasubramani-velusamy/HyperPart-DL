"""Interactive Plotly dashboards for HyperPart-DL visualization."""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict
import pandas as pd

from storage.node_simulation import StorageNode
from analytics.metrics import compute_replication_counts


def create_utilization_dashboard(nodes: List[StorageNode], replication_counts: Dict[str, int]) -> go.Figure:
    """Create interactive dashboard with node utilization and replication stats.
    
    Args:
        nodes: List of storage nodes.
        replication_counts: Dictionary of file label to replication count.
    
    Returns:
        Plotly Figure with subplots.
    """
    utilizations = [n.get_utilization() for n in nodes]
    node_ids = [n.node_id for n in nodes]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Node Utilizations", "Replication Distribution"),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Left: Node utilization
    fig.add_trace(
        go.Bar(x=node_ids, y=utilizations, name="Blocks", marker_color="steelblue",
               hovertemplate="<b>%{x}</b><br>Blocks: %{y}<extra></extra>"),
        row=1, col=1
    )
    
    # Right: Top replicated files
    top_files = sorted(replication_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    labels, counts = zip(*top_files) if top_files else ([], [])
    fig.add_trace(
        go.Bar(x=list(labels), y=list(counts), name="Replicas", marker_color="coral",
               hovertemplate="<b>%{x}</b><br>Replicas: %{y}<extra></extra>"),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Node", row=1, col=1)
    fig.update_xaxes(title_text="File Label", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=1)
    fig.update_yaxes(title_text="Replication Count", row=1, col=2)
    
    fig.update_layout(
        title_text="HyperPart-DL: Node Utilization & File Replication",
        height=500,
        showlegend=False,
        hovermode="x unified"
    )
    
    return fig


def create_metrics_timeseries(history: List[Dict]) -> go.Figure:
    """Create interactive time-series plot from simulation history.
    
    Args:
        history: List of metrics dictionaries from DynamicSimulation.
    
    Returns:
        Plotly Figure with multiple traces.
    """
    df = pd.DataFrame(history)
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Load Variance Over Time", "Deduplication Ratio Over Time"),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]],
        vertical_spacing=0.15
    )
    
    # Variance trace
    fig.add_trace(
        go.Scatter(x=df["step"], y=df["variance"], mode="lines+markers",
                   name="Variance", line=dict(color="red", width=2),
                   hovertemplate="Step %{x}<br>Variance: %{y:.3f}<extra></extra>"),
        row=1, col=1
    )
    
    # Dedup ratio trace
    fig.add_trace(
        go.Scatter(x=df["step"], y=df["dedup_ratio"], mode="lines+markers",
                   name="Dedup Ratio", line=dict(color="green", width=2),
                   hovertemplate="Step %{x}<br>Dedup Ratio: %{y:.3f}<extra></extra>"),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Time Step", row=1, col=1)
    fig.update_xaxes(title_text="Time Step", row=2, col=1)
    fig.update_yaxes(title_text="Variance", row=1, col=1)
    fig.update_yaxes(title_text="Dedup Ratio", row=2, col=1)
    
    fig.update_layout(
        title_text="Simulation Metrics Progression",
        height=700,
        hovermode="x unified",
        showlegend=True
    )
    
    return fig


def create_hypergraph_interactive(hg_model) -> go.Figure:
    """Create interactive hypergraph visualization using Plotly.
    
    Args:
        hg_model: HyperGraphModel instance.
    
    Returns:
        Plotly Figure showing network graph.
    """
    import networkx as nx
    
    G = hg_model.graph
    if not G.nodes():
        return go.Figure().add_annotation(text="Hypergraph is empty")
    
    # Use spring layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Extract edges
    edge_x = []
    edge_y = []
    edge_text = []
    
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
        shared_count = data.get("shared_count", 0)
        edge_text.append(f"{u} ↔ {v}: {shared_count} shared files")
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=2, color="gray"),
        hoverinfo="none",
        showlegend=False
    )
    
    # Extract nodes
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        util = G.nodes[node].get("utilization", 1)
        node_text.append(f"<b>{node}</b><br>Utilization: {util}")
        node_size.append(max(20, util * 15))
        node_color.append(util)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=[n for n in G.nodes()],
        textposition="top center",
        hoverinfo="text",
        hovertext=node_text,
        marker=dict(
            size=node_size,
            color=node_color,
            colorscale="Viridis",
            line=dict(width=2, color="navy"),
            showscale=True,
            colorbar=dict(title="Utilization"),
        ),
        showlegend=False
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="Interactive Hypergraph: Storage Nodes & Shared Files",
        showlegend=False,
        hovermode="closest",
        height=700,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    
    return fig


def generate_dashboard_html(nodes: List[StorageNode], replication_counts: Dict[str, int], 
                           hg_model, history: List[Dict] = None, output_file: str = "dashboard.html") -> str:
    """Generate a combined HTML dashboard with all interactive visualizations.
    
    Args:
        nodes: List of storage nodes.
        replication_counts: Dictionary of file replication counts.
        hg_model: HyperGraphModel instance.
        history: Optional simulation history for time-series plot.
        output_file: Output HTML file path.
    
    Returns:
        Path to the generated HTML file.
    """
    from plotly.subplots import make_subplots
    
    # Create individual figures
    util_fig = create_utilization_dashboard(nodes, replication_counts)
    hg_fig = create_hypergraph_interactive(hg_model)
    
    # Create a unified figure with subplots (simplified approach: use separate figures)
    # For a full dashboard, combine into one with tabs or sections
    
    with open(output_file, "w") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write('<meta charset="utf-8">\n')
        f.write("<title>HyperPart-DL Dashboard</title>\n")
        f.write('<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>\n')
        f.write("<style>\n")
        f.write("body { font-family: Arial, sans-serif; margin: 10px; }\n")
        f.write(".chart-container { margin: 20px 0; border: 1px solid #ccc; padding: 10px; }\n")
        f.write("</style>\n")
        f.write("</head>\n<body>\n")
        
        f.write("<h1>HyperPart-DL Interactive Dashboard</h1>\n")
        
        # Utilization & replication
        f.write("<div class='chart-container'>\n")
        f.write("<h2>Node Utilization & File Replication</h2>\n")
        f.write("<div id='util-chart'></div>\n")
        f.write("</div>\n")
        
        # Hypergraph
        f.write("<div class='chart-container'>\n")
        f.write("<h2>Storage Network (Hypergraph)</h2>\n")
        f.write("<div id='hg-chart'></div>\n")
        f.write("</div>\n")
        
        # Time-series if history provided
        if history:
            ts_fig = create_metrics_timeseries(history)
            f.write("<div class='chart-container'>\n")
            f.write("<h2>Metrics Over Time</h2>\n")
            f.write("<div id='ts-chart'></div>\n")
            f.write("</div>\n")
        
        # Embed scripts
        f.write("<script>\n")
        f.write(f"var utilData = {util_fig.to_json()};\n")
        f.write("Plotly.newPlot('util-chart', utilData.data, utilData.layout);\n")
        
        f.write(f"var hgData = {hg_fig.to_json()};\n")
        f.write("Plotly.newPlot('hg-chart', hgData.data, hgData.layout);\n")
        
        if history:
            ts_fig = create_metrics_timeseries(history)
            f.write(f"var tsData = {ts_fig.to_json()};\n")
            f.write("Plotly.newPlot('ts-chart', tsData.data, tsData.layout);\n")
        
        f.write("</script>\n")
        f.write("</body>\n</html>\n")
    
    return output_file
