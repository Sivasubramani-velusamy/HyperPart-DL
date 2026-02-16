from typing import List
import numpy as np
from storage.node_simulation import StorageNode


def calculate_load_variance(nodes: List[StorageNode]) -> float:
    counts = [n.get_utilization() for n in nodes]
    return float(np.var(counts))


def detect_imbalance(nodes: List[StorageNode], threshold: float = 1.0) -> bool:
    var = calculate_load_variance(nodes)
    return var > threshold


def rebalance(nodes: List[StorageNode]) -> bool:
    if not nodes:
        return False
    nodes_sorted = sorted(nodes, key=lambda n: n.get_utilization())
    least = nodes_sorted[0]
    most = nodes_sorted[-1]
    if most.get_utilization() - least.get_utilization() <= 1:
        return False
    block = most.remove_block()
    if block is None:
        return False
    block_hash, label = block
    least.store_block(block_hash, label)
    return True
