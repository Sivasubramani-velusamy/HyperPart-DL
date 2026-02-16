from typing import List
import numpy as np
from storage.node_simulation import StorageNode


def calculate_load_variance(nodes: List[StorageNode]) -> float:
    """Calculate the variance of block counts across nodes.
    
    A lower variance indicates better load balance. Variance of 0 means all
    nodes have identical utilization.
    
    Args:
        nodes: List of storage nodes to analyze.
    
    Returns:
        Variance of utilization counts across nodes.
    """
    counts = [n.get_utilization() for n in nodes]
    return float(np.var(counts))


def detect_imbalance(nodes: List[StorageNode], threshold: float = 1.0) -> bool:
    """Detect if the system is imbalanced based on variance threshold.
    
    Args:
        nodes: List of storage nodes to analyze.
        threshold: Variance threshold above which imbalance is detected. Defaults to 1.0.
    
    Returns:
        True if variance exceeds threshold (imbalanced), False otherwise.
    """
    var = calculate_load_variance(nodes)
    return var > threshold


def rebalance(nodes: List[StorageNode]) -> bool:
    """Perform one iteration of block rebalancing.
    
    Moves a single block from the most-loaded node to the least-loaded node
    if the difference is > 1 block. Returns early if nodes are balanced.
    
    Args:
        nodes: List of storage nodes to rebalance.
    
    Returns:
        True if a block was moved, False if already balanced or no blocks to move.
    """
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
