from typing import List, Optional
import matplotlib.pyplot as plt
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
