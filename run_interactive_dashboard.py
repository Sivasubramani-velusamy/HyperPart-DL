#!/usr/bin/env python3
"""Generate interactive Plotly dashboard from HyperPart-DL simulation."""

import csv
from main import main
from analytics.interactive_dashboard import generate_dashboard_html
from analytics.metrics import compute_replication_counts


def load_history_from_csv(filename: str = "simulation_metrics_history.csv") -> list:
    """Load simulation history from CSV file.
    
    Args:
        filename: Path to the metrics history CSV.
    
    Returns:
        List of dictionaries with metrics per step.
    """
    history = []
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert string values to numeric
                history.append({
                    'step': int(row['step']),
                    'variance': float(row['variance']),
                    'dedup_ratio': float(row['dedup_ratio']),
                    'space_saved_ratio': float(row['space_saved_ratio']),
                })
    except FileNotFoundError:
        print(f"Warning: {filename} not found. Dashboard will not include time-series.")
        history = None
    
    return history


def main_dashboard():
    """Main entry point for dashboard generation."""
    print("=" * 60)
    print("HyperPart-DL: Interactive Dashboard Generator")
    print("=" * 60)
    
    # Run the main simulation first
    print("\n[1/3] Running static simulation...")
    nodes, hg_model = main()
    print("[✓] Static simulation complete")
    
    # Compute replication counts
    print("\n[2/3] Computing metrics...")
    replication_counts = compute_replication_counts(nodes)
    print(f"[✓] Metrics computed: {len(replication_counts)} unique files")
    
    # Load simulation history
    print("\n[3/3] Loading simulation history...")
    history = load_history_from_csv()
    if history:
        print(f"[✓] Loaded history: {len(history)} time steps")
    else:
        print("[✓] No history file; dashboard will exclude time-series")
    
    # Generate dashboard
    print("\n[4/4] Generating interactive dashboard...")
    output_file = generate_dashboard_html(
        nodes=nodes,
        replication_counts=replication_counts,
        hg_model=hg_model,
        history=history,
        output_file="dashboard.html"
    )
    print(f"[✓] Dashboard generated: {output_file}")
    
    print("\n" + "=" * 60)
    print("SUCCESS: Dashboard ready at dashboard.html")
    print("Open in web browser to interact with visualizations")
    print("=" * 60)


if __name__ == "__main__":
    main_dashboard()
