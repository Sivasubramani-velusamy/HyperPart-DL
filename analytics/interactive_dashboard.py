"""Interactive Plotly dashboards for HyperPart-DL visualization."""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict
import pandas as pd

from storage.node_simulation import StorageNode
from analytics.metrics import compute_replication_counts
import json
import networkx as nx


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
    capacities = [n.get_capacity() for n in nodes]
    ratios = [n.get_utilization_ratio() for n in nodes]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Node Utilizations", "Replication Distribution"),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Left: Node utilization
    hover_texts = []
    for nid, util, cap, r in zip(node_ids, utilizations, capacities, ratios):
        if cap is None:
            hover_texts.append(f"{nid}<br>Blocks: {util}<br>Capacity: unlimited")
        else:
            hover_texts.append(f"{nid}<br>Blocks: {util}/{cap} ({r*100:.0f}%)")

    fig.add_trace(
        go.Bar(x=node_ids, y=utilizations, name="Blocks", marker_color="steelblue", hovertext=hover_texts, hoverinfo='text'),
        row=1, col=1
    )

    # Right: replication distribution
    rep_labels = list(replication_counts.keys())
    rep_values = list(replication_counts.values())
    fig.add_trace(
        go.Bar(x=rep_labels, y=rep_values, name="Replications", marker_color="indianred"),
        row=1, col=2
    )

    fig.update_layout(title="Node Utilization & Replication", showlegend=False, height=450)
    return fig


def create_hypergraph_interactive(hg_model) -> go.Figure:
    """Create an interactive hypergraph figure from a HyperGraphModel or NetworkX graph."""
    # Accept either a HyperGraphModel instance or a NetworkX Graph
    G = getattr(hg_model, "graph", hg_model)
    pos = nx.spring_layout(G, seed=42)

    # build edge coordinates and hover text
    edge_x = []
    edge_y = []
    edge_text = []
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        shared_count = data.get("shared_count", 0)
        edge_text.append(f"{u} ↔ {v}: {shared_count} shared files")

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=2, color="gray"),
        hoverinfo="text",
        text=edge_text,
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
        cap = G.nodes[node].get("capacity", None)
        if cap is None:
            txt = f"<b>{node}</b><br>Utilization: {util}<br>Capacity: unlimited"
            clr = util
        else:
            ratio = util / float(cap) if cap > 0 else 0.0
            txt = f"<b>{node}</b><br>Utilization: {util}/{cap} ({ratio*100:.0f}%)"
            clr = ratio
        node_text.append(txt)
        node_size.append(max(20, util * 15))
        node_color.append(clr)

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


def create_animated_file_replication(history: List[Dict], output_height: int = 700) -> go.Figure:
    """Create an animated bipartite visualization of nodes <-> files over time.

    Expects each history entry to contain a `placement` dict mapping node_id -> [labels]
    and `failed_node_ids` list.
    """
    # collect all nodes and files across history
    if not history:
        return go.Figure().add_annotation(text="No history available for animation")

    all_nodes = []
    all_files = set()
    for h in history:
        for nid, labels in h.get("placement", {}).items():
            if nid not in all_nodes:
                all_nodes.append(nid)
            for lab in labels:
                all_files.add(lab)
    all_files = sorted(list(all_files))

    # layout positions: nodes on top row, files on bottom row
    n = len(all_nodes)
    m = len(all_files)
    node_x = [i * 1.0 for i in range(n)]
    node_y = [1.0] * n
    file_x = [i * 1.0 for i in range(m)]
    file_y = [0.0] * m

    # base traces: nodes and files (markers)
    node_trace = go.Scatter(x=node_x, y=node_y, mode="markers+text", text=all_nodes,
                            marker=dict(size=30, color="steelblue"), textposition="top center",
                            hoverinfo="text")
    file_trace = go.Scatter(x=file_x, y=file_y, mode="markers+text", text=all_files,
                            marker=dict(size=18, color="lightgray"), textposition="bottom center",
                            hoverinfo="text")

    frames = []
    # create frames for each time step
    for step_data in history:
        step = step_data.get("step")
        placement = step_data.get("placement", {})
        failed = set(step_data.get("failed_node_ids", []))

        # build edge coordinates
        edge_x = []
        edge_y = []
        for ni, nid in enumerate(all_nodes):
            labels = placement.get(nid, [])
            for lab in labels:
                if lab in all_files:
                    fi = all_files.index(lab)
                    edge_x += [node_x[ni], file_x[fi], None]
                    edge_y += [node_y[ni], file_y[fi], None]

        # node colors reflect failed status
        node_colors = ["crimson" if nid in failed else "steelblue" for nid in all_nodes]

        frame = go.Frame(data=[
            go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(color="gray", width=2), hoverinfo="none"),
            go.Scatter(x=node_x, y=node_y, mode="markers+text", marker=dict(size=30, color=node_colors), text=all_nodes, textposition="top center", hoverinfo="text"),
            go.Scatter(x=file_x, y=file_y, mode="markers+text", marker=dict(size=18, color="lightgray"), text=all_files, textposition="bottom center", hoverinfo="text"),
        ], name=str(step), layout=go.Layout(title_text=f"File replication - step {step}"))
        frames.append(frame)

    # initial data = first frame
    fig = go.Figure(data=frames[0].data, frames=frames)
    fig.update_layout(
        title=f"File-Node Replication Animation (steps: {len(frames)})",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=output_height,
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": 700, "redraw": True}, "fromcurrent": True}]},
                {"label": "Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]}
            ]
        }],
        sliders=[{
            "steps": [{"method": "animate", "label": f.get("name"), "args": [[f.get("name")], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]} for f in frames],
            "currentvalue": {"prefix": "Step: "}
        }]
    )

    return fig


def create_metrics_timeseries(history: List[Dict]) -> go.Figure:
    """Create a Plotly time-series figure for simulation metrics stored in history.

    Expects history to be a list of dicts with keys like 'step', 'total_blocks',
    'unique_blocks', 'avg_replication', 'active_nodes', 'failed_nodes'.
    """
    if not history:
        return go.Figure().add_annotation(text="No history available")

    steps = [h.get('step', i) for i, h in enumerate(history)]
    total = [h.get('total_blocks', None) for h in history]
    unique = [h.get('unique_blocks', None) for h in history]
    avg_rep = [h.get('avg_replication', None) for h in history]
    active = [h.get('active_nodes', None) for h in history]
    failed = [h.get('failed_nodes', 0) for h in history]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
                        subplot_titles=("Blocks & Replication", "Node Availability"))

    fig.add_trace(go.Scatter(x=steps, y=total, mode='lines+markers', name='Total Blocks', marker=dict(color='steelblue')),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=steps, y=unique, mode='lines+markers', name='Unique Blocks', marker=dict(color='green')),
                  row=1, col=1)
    fig.add_trace(go.Bar(x=steps, y=avg_rep, name='Avg Replication', marker_color='indianred', opacity=0.6), row=1, col=1)

    fig.add_trace(go.Scatter(x=steps, y=active, mode='lines+markers', name='Active Nodes', marker=dict(color='darkblue')),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=steps, y=failed, mode='lines+markers', name='Failed Nodes', marker=dict(color='crimson')),
                  row=2, col=1)

    fig.update_layout(height=500, showlegend=True, title_text='Simulation Metrics Over Time')
    fig.update_xaxes(title_text='Step', row=2, col=1)
    fig.update_yaxes(title_text='Blocks / Replication', row=1, col=1)
    fig.update_yaxes(title_text='Node count', row=2, col=1)
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
        # Animated file replication (if placement snapshots available)
        if history and all('placement' in h for h in history):
            f.write("<div class='chart-container'>\n")
            f.write("<h2>Animated File Replication (Nodes ↔ Files)</h2>\n")
            f.write("<div id='anim-chart'></div>\n")
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
        if history and all('placement' in h for h in history):
            anim_fig = create_animated_file_replication(history)
            f.write(f"var animData = {anim_fig.to_json()};\n")
            # use frames and layout to create animation
            f.write("Plotly.newPlot('anim-chart', animData.data, animData.layout).then(function() { Plotly.addFrames('anim-chart', animData.frames); });\n")
        
        f.write("</script>\n")
        f.write("</body>\n</html>\n")
    
    return output_file
