from typing import List
import networkx as nx
from storage.node_simulation import StorageNode


class HyperGraphModel:
    """Represents a hypergraph of storage nodes connected by shared replicated files.
    
    A node is added to the graph for each storage node. Edges are created between
    nodes that share at least one replicated file label, with metadata about
    the shared files.
    
    Attributes:
        graph: NetworkX undirected graph. Nodes are storage node IDs, edges
               represent shared file relationships.
    """

    def __init__(self) -> None:
        """Initialize an empty hypergraph."""
        self.graph = nx.Graph()

    def add_storage_nodes(self, nodes: List[StorageNode]) -> None:
        """Add storage nodes to the hypergraph.
        
        Each node is added with a 'utilization' attribute reflecting its
        current block count.
        
        Args:
            nodes: List of StorageNode instances to add.
        """
        for n in nodes:
            self.graph.add_node(n.node_id, utilization=n.get_utilization())

    def connect_nodes_by_shared_files(self, nodes: List[StorageNode]) -> None:
        """Create edges between nodes that share replicated file labels.
        
        An edge is created between two nodes if they share at least one
        file label. The edge includes metadata about the shared files:
        shared_count and shared_labels.
        
        Args:
            nodes: List of StorageNode instances to connect.
        """
        # Create edges between nodes that share at least one replicated label
        labels_by_node = {n.node_id: set(n.get_labels()) for n in nodes}
        node_ids = list(labels_by_node.keys())
        for i in range(len(node_ids)):
            for j in range(i + 1, len(node_ids)):
                a = node_ids[i]
                b = node_ids[j]
                shared = labels_by_node[a].intersection(labels_by_node[b])
                if shared:
                    self.graph.add_edge(a, b, shared_count=len(shared), shared_labels=list(shared))

    def display_info(self) -> None:
        """Print a summary of hypergraph structure (nodes and edges)."""
        print("Hypergraph nodes:")
        for n, data in self.graph.nodes(data=True):
            print(f"  - {n}: {data}")
        print("Hypergraph edges:")
        for a, b, data in self.graph.edges(data=True):
            print(f"  - {a} <-> {b}: {data}")
