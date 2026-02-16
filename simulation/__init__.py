from typing import List, Dict
from storage.node_simulation import StorageNode
from deduplication.hashing import generate_hash
from repartition.optimizer import calculate_load_variance, detect_imbalance, rebalance
from analytics.metrics import compute_replication_counts, calculate_deduplication_savings
import random


class DynamicSimulation:
    """Simulate dynamic workload: files added/removed over time steps.
    
    Tracks metrics progression (variance, dedup ratio, replication) across steps.
    """

    def __init__(self, num_nodes: int = 3, replication_factor: int = 2, seed: int = 42, capacities: List[int] = None):
        """Initialize simulation.
        
        Args:
            num_nodes: Number of storage nodes.
            replication_factor: Number of replicas per unique file.
            seed: Random seed for reproducibility.
        """
        random.seed(seed)
        # create nodes, optionally with heterogeneous capacities
        if capacities and len(capacities) >= num_nodes:
            self.nodes = [StorageNode(f"N{i}", capacity=capacities[i-1]) for i in range(1, num_nodes + 1)]
        else:
            self.nodes = [StorageNode(f"N{i}") for i in range(1, num_nodes + 1)]
        self.replication_factor = replication_factor
        self.history: List[Dict] = []
        self.all_files: Dict[str, bytes] = {}
        # Track failed nodes (node_id -> StorageNode)
        self.failed_nodes: Dict[str, StorageNode] = {}

    def add_files(self, new_files: Dict[str, bytes]) -> None:
        """Add new files to the system and distribute replicas.
        
        Args:
            new_files: Dictionary of {label: content} to add.
        """
        hash_to_label: Dict[str, str] = {}
        for label, content in new_files.items():
            h = generate_hash(content, algorithm="sha256")
            if h not in hash_to_label:
                hash_to_label[h] = label
                self.all_files[label] = content

        for block_hash, label in hash_to_label.items():
            # place replicas while respecting capacity and avoiding duplicates on same node
            placed = 0
            candidates = [n for n in self.nodes if label not in n.get_labels() and (n.remaining_capacity() is None or n.remaining_capacity() > 0)]
            while placed < min(self.replication_factor, len(self.nodes)) and candidates:
                target = random.choice(candidates)
                ok = target.store_block(block_hash, label)
                if ok:
                    placed += 1
                # refresh candidates
                candidates = [n for n in self.nodes if label not in n.get_labels() and (n.remaining_capacity() is None or n.remaining_capacity() > 0)]

    def remove_random_files(self, num_to_remove: int) -> None:
        """Randomly remove files from nodes to simulate churn.
        
        Args:
            num_to_remove: Number of blocks to remove.
        """
        removed = 0
        for _ in range(min(num_to_remove, sum(n.get_utilization() for n in self.nodes))):
            node = random.choice(self.nodes)
            if node.remove_block():
                removed += 1


    def rebalance_system(self, threshold: float = 1.0, max_iterations: int = 10) -> int:
        """Detect and rebalance if imbalanced.
        
        Args:
            threshold: Variance threshold for imbalance detection.
            max_iterations: Max rebalance iterations.
        
        Returns:
            Number of blocks moved.
        """
        if not detect_imbalance(self.nodes, threshold):
            return 0
        moved = 0
        for _ in range(max_iterations):
            if rebalance(self.nodes):
                moved += 1
            else:
                break
        return moved

    def fail_node(self, node_id: str) -> bool:
        """Simulate node failure: remove node from active list and redistribute its blocks.

        Args:
            node_id: Identifier of the node to fail.

        Returns:
            True if a node was failed, False otherwise.
        """
        # find node
        node = next((n for n in self.nodes if n.node_id == node_id), None)
        if not node:
            return False

        # remove from active nodes and store in failed_nodes
        self.nodes = [n for n in self.nodes if n.node_id != node_id]
        self.failed_nodes[node_id] = node

        # redistribute blocks previously on failed node to maintain replication factor
        rep_counts = compute_replication_counts(self.nodes)
        for h, label in node.data_blocks:
            count = rep_counts.get(label, 0)
            while count < self.replication_factor:
                # pick a node that doesn't already have this label
                candidates = [n for n in self.nodes if label not in n.get_labels()]
                if not candidates:
                    break
                target = random.choice(candidates)
                target.store_block(h, label)
                count += 1
                rep_counts[label] = count

        print(f"Node {node_id} failed — redistributed its blocks")
        return True

    def recover_node(self, node_id: str) -> bool:
        """Recover a previously failed node, re-add it to active nodes and rebalance.

        Args:
            node_id: Identifier of the node to recover.

        Returns:
            True if recovery succeeded, False otherwise.
        """
        node = self.failed_nodes.pop(node_id, None)
        if not node:
            return False

        # re-add node to active list
        self.nodes.append(node)
        # On recovery, rebalance to spread load evenly
        moved = self.rebalance_system()
        print(f"Node {node_id} recovered — rebalanced ({moved} moves)")
        return True

    def record_metrics(self, step: int) -> Dict:
        """Compute and record metrics for current state.
        
        Args:
            step: Time step number.
        
        Returns:
            Dictionary of metrics for this step.
        """
        total_blocks = sum(n.get_utilization() for n in self.nodes)
        unique_blocks = len(set(label for n in self.nodes for label in n.get_labels()))
        var = calculate_load_variance(self.nodes)
        rep_counts = compute_replication_counts(self.nodes)
        avg_rep = sum(rep_counts.values()) / len(rep_counts) if rep_counts else 0
        dedup_info = calculate_deduplication_savings(len(self.all_files), unique_blocks, self.replication_factor)

        # capture placement snapshot: node_id -> list of labels
        placement = {n.node_id: list(n.get_labels()) for n in self.nodes}
        failed_ids = list(self.failed_nodes.keys())

        metrics = {
            "step": step,
            "total_blocks": total_blocks,
            "unique_blocks": unique_blocks,
            "variance": var,
            "avg_replication": avg_rep,
            "dedup_ratio": dedup_info["dedup_ratio"],
            "space_saved_ratio": dedup_info["space_saved_ratio"],
            "placement": placement,
            "failed_node_ids": failed_ids,
            "active_nodes": len(self.nodes),
            "failed_nodes": len(self.failed_nodes),
        }
        self.history.append(metrics)
        return metrics

    def run_simulation(self, steps: int = 5) -> List[Dict]:
        """Run multi-step simulation.
        
        Each step: add files, possibly rebalance, record metrics.
        
        Args:
            steps: Number of time steps to simulate.
        
        Returns:
            List of metrics dictionaries for each step.
        """
        # schedule: fail at middle step, recover at final step
        failure_step = max(1, steps // 2)
        recovery_step = steps - 1

        for step in range(steps):
            print(f"\n--- Step {step} ---")

            # Add some new files
            new_files = {
                f"step{step}_file{i}.txt": f"content_{step}_{i}".encode()
                for i in range(2)
            }
            self.add_files(new_files)
            print(f"Added {len(new_files)} new files")

            # Randomly remove some blocks to simulate churn
            if step > 0:
                self.remove_random_files(num_to_remove=1)
                print("Removed 1 random block")

            # Simulate node failure at scheduled step
            if step == failure_step and self.nodes:
                # choose a random active node to fail
                victim = random.choice(self.nodes)
                self.fail_node(victim.node_id)

            # Simulate recovery at scheduled step
            if step == recovery_step and self.failed_nodes:
                # recover one failed node (pick arbitrary)
                to_recover = next(iter(self.failed_nodes.keys()))
                self.recover_node(to_recover)

            # Rebalance if needed
            moved = self.rebalance_system(threshold=1.0)
            if moved > 0:
                print(f"Rebalanced: moved {moved} block(s)")

            # Record metrics
            metrics = self.record_metrics(step)
            print(f"Metrics: variance={metrics['variance']:.3f}, dedup_ratio={metrics['dedup_ratio']:.3f}, "
                  f"space_saved={metrics['space_saved_ratio']*100:.1f}%")

        return self.history
