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
    # Sort by utilization ratio (blocks / capacity) when capacities vary
    def util_key(n: StorageNode) -> float:
        return n.get_utilization_ratio()

    nodes_sorted = sorted(nodes, key=util_key)
    least = nodes_sorted[0]
    most = nodes_sorted[-1]

    # Only move if donor is noticeably more utilized than recipient
    if util_key(most) - util_key(least) <= 0.05:
        return False

    # Attempt to move one block from most to least (or another candidate with capacity)
    block = most.remove_block()
    if block is None:
        return False
    block_hash, label = block

    # try primary target first
    candidates = [n for n in nodes_sorted if n.remaining_capacity() != 0 and label not in n.get_labels()]
    # prefer least-utilized first
    candidates = sorted(candidates, key=util_key)
    for target in candidates:
        if target.store_block(block_hash, label):
            return True

    # if no candidate accepted block, put it back to the donor
    most.store_block(block_hash, label)
    return False
