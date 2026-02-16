from typing import List, Optional
import matplotlib.pyplot as plt
import networkx as nx
from storage.node_simulation import StorageNode


def plot_utilization(nodes: List[StorageNode], save_path: Optional[str] = "utilization.png") -> None:
    ids = [n.node_id for n in nodes]
    vals = [n.get_utilization() for n in nodes]
    plt.figure(figsize=(6, 4))
    bars = plt.bar(ids, vals, color="tab:blue")
    plt.xlabel("Node")
    plt.ylabel("Utilization (blocks)")
    plt.title("Node Utilizations")
    for b, v in zip(bars, vals):
        plt.text(b.get_x() + b.get_width() / 2, v + 0.1, str(v), ha="center", va="bottom")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.close()


def plot_replication_distribution(replication_counts: dict, save_path: Optional[str] = "replication_distribution.png") -> None:
    labels = list(replication_counts.keys())
    vals = [replication_counts[k] for k in labels]
    plt.figure(figsize=(8, 4))
    bars = plt.bar(labels, vals, color="tab:orange")
    plt.xlabel("Label")
    plt.ylabel("Replication Count")
    plt.title("Replication Distribution")
    plt.xticks(rotation=45, ha="right")
    for b, v in zip(bars, vals):
        plt.text(b.get_x() + b.get_width() / 2, v + 0.05, str(v), ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.close()


def plot_hypergraph(hg_model, save_path: Optional[str] = "hypergraph.png") -> None:
    """Visualize the hypergraph of storage nodes and shared file connections.
    
    Nodes are sized by utilization; edges are labeled with shared file counts.
    
    Args:
        hg_model: HyperGraphModel instance with graph attribute.
        save_path: Path to save the figure; if None, does not save.
    """
    G = hg_model.graph
    if not G.nodes():
        print("Hypergraph is empty; skipping visualization.")
        return

    plt.figure(figsize=(10, 8))
    
    # Use spring layout for better visualization
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Node sizes based on utilization
    node_sizes = [G.nodes[node].get("utilization", 1) * 300 for node in G.nodes()]
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="lightblue", 
                          edgecolors="navy", linewidths=2)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.6, edge_color="gray")
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")
    
    # Draw edge labels (shared file count)
    edge_labels = {(u, v): d.get("shared_count", 0) for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=9)
    
    plt.title("Hypergraph: Storage Nodes & Shared Files")
    plt.axis("off")
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
