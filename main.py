import random
from typing import Dict, List

random.seed(42)

from storage.node_simulation import StorageNode
from deduplication.hashing import generate_hash
from repartition.optimizer import calculate_load_variance, detect_imbalance, rebalance
from hypergraph.hypergraph_model import HyperGraphModel
from analytics.visualization import plot_utilization, plot_replication_distribution, plot_hypergraph
from analytics.metrics import compute_replication_counts, node_unique_counts, top_replicated, export_metrics_csv, calculate_deduplication_savings
import os


def main() -> None:
    """
    Main simulation pipeline for HyperPart-DL.
    
    Creates a distributed storage system with:
    - 3 storage nodes
    - 8 files with duplicates
    - Global deduplication
    - Replication factor of 2
    - Imbalance detection and rebalancing
    - Hypergraph modeling
    - Metrics and visualization
    """
    # create nodes
    nodes: List[StorageNode] = [StorageNode(f"N{i}") for i in range(1, 4)]

    # simulate dataset with duplicates
    files = {
        "file_a.txt": b"alpha data",
        "file_b.txt": b"beta data",
        "file_c.txt": b"gamma data",
        "file_d.txt": b"alpha data",  # duplicate of a
        "file_e.txt": b"delta data",
        "file_f.txt": b"beta data",   # duplicate of b
        "file_g.txt": b"epsilon data",
        "file_h.txt": b"zeta data",
    }

    original_blocks = len(files)

    # deduplicate globally
    hash_to_label: Dict[str, str] = {}
    for label, content in files.items():
        h = generate_hash(content, algorithm="sha256")
        if h not in hash_to_label:
            hash_to_label[h] = label

    unique_blocks = len(hash_to_label)
    dedup_ratio = original_blocks / unique_blocks if unique_blocks else 0

    # replication factor = 2
    replication_factor = 2
    hashes = list(hash_to_label.items())  # (hash, label)
    # distribute each unique block to replication_factor distinct nodes
    for block_hash, label in hashes:
        chosen = random.sample(nodes, k=min(replication_factor, len(nodes)))
        for n in chosen:
            n.store_block(block_hash, label)

    print("Utilizations before rebalancing:")
    for n in nodes:
        print(f"  {n.node_id}: {n.get_utilization()}")

    # visualize optionally
    try:
        plot_utilization(nodes)
    except Exception:
        pass

    # detect imbalance and rebalance
    var_before = calculate_load_variance(nodes)
    print(f"Load variance before: {var_before:.3f}")
    if detect_imbalance(nodes, threshold=1.0):
        # rebalance until balanced or limited iterations
        for _ in range(10):
            changed = rebalance(nodes)
            if not changed:
                break
    var_after = calculate_load_variance(nodes)

    print("Utilizations after rebalancing:")
    for n in nodes:
        print(f"  {n.node_id}: {n.get_utilization()}")
    print(f"Load variance after: {var_after:.3f}")

    print(f"Deduplication ratio (original/unique): {dedup_ratio:.3f} ({original_blocks}/{unique_blocks})")

    # build hypergraph
    hg = HyperGraphModel()
    hg.add_storage_nodes(nodes)
    hg.connect_nodes_by_shared_files(nodes)
    hg.display_info()

    # visualize hypergraph
    try:
        plot_hypergraph(hg)
    except Exception as e:
        print(f"Failed to visualize hypergraph: {e}")

    # additional analytics / metrics
    replication_counts = compute_replication_counts(nodes)
    node_counts = node_unique_counts(nodes)
    top5 = top_replicated(replication_counts, top=5)
    dedup_savings = calculate_deduplication_savings(original_blocks, unique_blocks, replication_factor)

    print("\nReplication counts (label: count):")
    for label, cnt in replication_counts.items():
        print(f"  - {label}: {cnt}")

    print("\nTop replicated files:")
    for label, cnt in top5:
        print(f"  - {label}: {cnt}")

    print("\nDeduplication Savings:")
    print(f"  - Dedup ratio: {dedup_savings['dedup_ratio']:.3f}")
    print(f"  - Original blocks: {dedup_savings['original_raw_blocks']}")
    print(f"  - Unique blocks: {dedup_savings['deduplicated_blocks']}")
    print(f"  - With replication (factor {replication_factor}): {dedup_savings['with_replication']:.0f}")
    print(f"  - Space saved: {dedup_savings['space_saved_ratio']*100:.1f}%")

    # save replication plot and export CSV metrics
    try:
        plot_replication_distribution(replication_counts)
        rep_csv, node_csv = export_metrics_csv(replication_counts, node_counts, path_prefix="metrics")
        print(f"\nSaved metrics: {os.path.abspath(rep_csv)}, {os.path.abspath(node_csv)}")
    except Exception as e:
        print("Failed to save metrics/plots:", e)


if __name__ == "__main__":
    main()
