#!/usr/bin/env python3
"""Run a heterogeneous-capacity simulation and generate outputs.

Demonstrates nodes with different capacities and exports CSV/plots.
"""
import csv
from simulation import DynamicSimulation
from analytics.visualization import plot_utilization
from analytics.metrics import compute_replication_counts, node_unique_counts, export_metrics_csv


def run_hetero():
    # example capacities: N1=5, N2=3, N3=8
    capacities = [5, 3, 8]
    sim = DynamicSimulation(num_nodes=3, replication_factor=2, seed=42, capacities=capacities)
    print("Running heterogeneous capacity simulation...")
    history = sim.run_simulation(steps=5)

    # save history
    csv_path = "hetero_simulation_history.csv"
    if history:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=history[0].keys())
            writer.writeheader()
            writer.writerows(history)
        print(f"Saved history to {csv_path}")

    # generate plots and metrics
    nodes = sim.nodes
    rep_counts = compute_replication_counts(nodes)
    node_counts = node_unique_counts(nodes)
    plot_utilization(nodes, save_path="hetero_utilization.png")
    export_metrics_csv(rep_counts, node_counts, path_prefix="hetero_metrics", nodes=nodes)
    print("Outputs: hetero_utilization.png, hetero_metrics_*.csv")


if __name__ == '__main__':
    run_hetero()
