"""Dynamic workload simulation runner with metrics tracking over time."""

import csv
from simulation import DynamicSimulation


def run_dynamic_simulation():
    """Run a dynamic simulation and export metrics history to CSV."""
    sim = DynamicSimulation(num_nodes=3, replication_factor=2, seed=42)
    print("Starting dynamic workload simulation...\n")

    # Run 5 time steps
    history = sim.run_simulation(steps=5)

    # Export metrics history to CSV
    csv_path = "simulation_metrics_history.csv"
    if history:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=history[0].keys())
            writer.writeheader()
            writer.writerows(history)
        print(f"\nSaved metrics history to {csv_path}")

    print("\n--- Final Summary ---")
    print(f"Simulation steps: {len(history)}")
    if history:
        first = history[0]
        last = history[-1]
        print(f"Step 0: variance={first['variance']:.3f}, dedup_ratio={first['dedup_ratio']:.3f}")
        print(f"Step {len(history)-1}: variance={last['variance']:.3f}, dedup_ratio={last['dedup_ratio']:.3f}")


if __name__ == "__main__":
    run_dynamic_simulation()
