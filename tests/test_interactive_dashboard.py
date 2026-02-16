import os
import tempfile
from analytics import interactive_dashboard as iad
from storage.node_simulation import StorageNode


def make_node(node_id, labels, capacity=None):
    n = StorageNode(node_id=node_id, capacity=capacity)
    for l in labels:
        n.store_block(l)
    return n


def test_import_and_generate_minimal_dashboard(tmp_path):
    # Create minimal nodes
    n1 = make_node('T1', ['a','b'])
    n2 = make_node('T2', ['b','c'])
    nodes = [n1, n2]
    rep = iad.compute_replication_counts(nodes) if hasattr(iad, 'compute_replication_counts') else { 'a':1, 'b':2, 'c':1 }

    # Create a tiny history
    history = [
        {'step': 0, 'placement': {'T1':['a','b'], 'T2':['b','c']}, 'total_blocks':3, 'unique_blocks':3, 'avg_replication':1.0, 'active_nodes':2, 'failed_nodes':0},
    ]

    out = tmp_path / 'test_dash.html'
    path = iad.generate_dashboard_html(nodes, rep, None, history=history, output_file=str(out))
    assert os.path.exists(path)
    # ensure key functions exist
    assert hasattr(iad, 'create_utilization_dashboard')
    assert hasattr(iad, 'create_hypergraph_interactive')
    assert hasattr(iad, 'create_metrics_timeseries')
