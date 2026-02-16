"""Metrics helpers for HyperPart-DL.

This module provides functions to compute replication counts, per-node
unique counts, top-replicated files, deduplication savings calculations,
and export helpers for writing metrics to CSV files.
"""

from typing import Dict, List, Tuple, Optional
import csv

from storage.node_simulation import StorageNode


def compute_replication_counts(nodes: List[StorageNode]) -> Dict[str, int]:
    """Count how many times each unique file label appears across all nodes.
    
    Args:
        nodes: List of storage nodes.
    
    Returns:
        Dictionary mapping file label to its replication count.
    """
    counts: Dict[str, int] = {}
    for n in nodes:
        for label in n.get_labels():
            counts[label] = counts.get(label, 0) + 1
    return counts


def node_unique_counts(nodes: List[StorageNode]) -> Dict[str, int]:
    """Count unique file labels per node.
    
    Args:
        nodes: List of storage nodes.
    
    Returns:
        Dictionary mapping node ID to count of unique file labels on that node.
    """
    return {n.node_id: len(set(n.get_labels())) for n in nodes}


def top_replicated(replication_counts: Dict[str, int], top: int = 5) -> List[Tuple[str, int]]:
    """Get the most-replicated files.
    
    Args:
        replication_counts: Dictionary mapping labels to replication counts.
        top: Number of top files to return. Defaults to 5.
    
    Returns:
        List of (label, count) tuples sorted by count descending.
    """
    return sorted(replication_counts.items(), key=lambda x: x[1], reverse=True)[:top]


def calculate_deduplication_savings(original_count: int, unique_count: int, replication_factor: float = 1.0) -> Dict[str, float]:
    """Calculate storage savings achieved through deduplication and replication.
    
    Args:
        original_count: Total number of original blocks (before deduplication).
        unique_count: Number of unique blocks (after deduplication).
        replication_factor: Average replication factor (replicas per unique block).
    
    Returns:
        Dictionary with keys:
            - "dedup_ratio": original / unique (> 1 means savings)
            - "original_raw_blocks": original count
            - "deduplicated_blocks": unique count
            - "with_replication": unique * replication_factor (total blocks stored)
            - "space_saved_ratio": (1 - deduplicated/original) percentage
    """
    if unique_count == 0:
        return {
            "dedup_ratio": 0.0,
            "original_raw_blocks": original_count,
            "deduplicated_blocks": 0,
            "with_replication": 0.0,
            "space_saved_ratio": 0.0,
        }
    dedup_ratio = original_count / unique_count
    with_repl = unique_count * replication_factor
    space_saved = 1.0 - (unique_count / original_count)
    return {
        "dedup_ratio": dedup_ratio,
        "original_raw_blocks": original_count,
        "deduplicated_blocks": unique_count,
        "with_replication": with_repl,
        "space_saved_ratio": space_saved,
    }


def export_metrics_csv(replication_counts: Dict[str, int], node_counts: Dict[str, int], path_prefix: str = "metrics", nodes: Optional[List[StorageNode]] = None) -> Tuple[str, str]:
    """Export replication and node metrics to CSV files.
    
    Args:
        replication_counts: Dictionary mapping labels to replication counts.
        node_counts: Dictionary mapping node IDs to unique file counts.
        path_prefix: Prefix for output CSV file names. Defaults to "metrics".
    
    Returns:
        Tuple of (replication_csv_path, node_csv_path).
    """
    rep_path = f"{path_prefix}_replication_counts.csv"
    node_path = f"{path_prefix}_node_counts.csv"

    with open(rep_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "replication_count"])
        for label, cnt in sorted(replication_counts.items(), key=lambda x: x[0]):
            writer.writerow([label, cnt])

    with open(node_path, "w", newline="", encoding="utf-8") as f:
        # If full node objects provided, include capacity and utilization
        if nodes is not None:
            writer = csv.writer(f)
            writer.writerow(["node_id", "unique_labels", "utilization", "capacity", "util_ratio"])
            node_map = {n.node_id: n for n in nodes}
            for node_id, cnt in sorted(node_counts.items(), key=lambda x: x[0]):
                n = node_map.get(node_id)
                util = n.get_utilization() if n else cnt
                cap = n.get_capacity() if n else None
                util_ratio = n.get_utilization_ratio() if n else 0.0
                writer.writerow([node_id, cnt, util, cap if cap is not None else "unlimited", f"{util_ratio:.3f}"])
        else:
            writer = csv.writer(f)
            writer.writerow(["node_id", "unique_labels"])
            for node, cnt in sorted(node_counts.items(), key=lambda x: x[0]):
                writer.writerow([node, cnt])

    return rep_path, node_path
