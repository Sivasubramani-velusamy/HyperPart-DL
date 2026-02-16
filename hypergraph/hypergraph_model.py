from typing import List
import networkx as nx
from storage.node_simulation import StorageNode


class HyperGraphModel:
    def __init__(self) -> None:
        self.graph = nx.Graph()

    def add_storage_nodes(self, nodes: List[StorageNode]) -> None:
        for n in nodes:
            self.graph.add_node(n.node_id, utilization=n.get_utilization())

    def connect_nodes_by_shared_files(self, nodes: List[StorageNode]) -> None:
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
        print("Hypergraph nodes:")
        for n, data in self.graph.nodes(data=True):
            print(f"  - {n}: {data}")
        print("Hypergraph edges:")
        for a, b, data in self.graph.edges(data=True):
            print(f"  - {a} <-> {b}: {data}")
