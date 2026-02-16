# HyperPart-DL

**Distributed Storage Simulation with Deduplication, Load Balancing, and Hypergraph Modeling**

Lightweight Python framework for simulating distributed storage systems with focus on content-based deduplication, load imbalance detection/rebalancing, and hypergraph modeling of replicated files.

---

## Quick Start

### Prerequisites
- Python 3.11+ (LTS recommended)
- pip (comes with Python)
- Git (optional, for version control)

### Setup (Windows)

1. **Create and activate virtual environment:**
```bash
py -3.11 -m venv .venv311
.\.venv311\Scripts\activate
```

2. **Install dependencies:**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. **Run the main simulation:**
```bash
python main.py
```

4. **(Optional) Generate interactive dashboard:**
```bash
python run_interactive_dashboard.py
```

5. **(Optional) Run dynamic workload simulation:**
```bash
python run_dynamic_simulation.py
```

---

## System Architecture

### Data Flow Pipeline

```
Files (8 samples)
  ↓
Deduplication (SHA256 hashing)
  ↓
Unique Blocks (6 after dedup)
  ↓
Distribution (replication factor = 2)
  ↓
Storage Nodes (N1, N2, N3)
  ↓
Load Balance Detection
  ↓
Rebalance if Imbalanced
  ↓
Hypergraph Construction
  ↓
Analytics & Metrics
  ↓
Visualization (PNG + HTML + CSV)
```

### Module Architecture

```
main.py (Orchestrator)
  ├── storage/node_simulation.py
  │   └── StorageNode class: store/remove/utilization methods
  │
  ├── deduplication/hashing.py
  │   └── generate_hash(): SHA256/SHA1 content-based dedup
  │
  ├── repartition/optimizer.py
  │   └── variance calculation & block rebalancing
  │
  ├── hypergraph/hypergraph_model.py
  │   └── HyperGraphModel: NetworkX graph of shared files
  │
  ├── analytics/metrics.py
  │   └── compute_replication_counts() & export CSV
  │
  ├── analytics/visualization.py
  │   └── plot_utilization(), plot_replication_distribution()
  │
  ├── analytics/interactive_dashboard.py
  │   └── Plotly: interactive charts with hover tooltips
  │
  └── simulation/__init__.py
      └── DynamicSimulation: multi-step workload
```

---

## Core Concepts

### 1. Deduplication
- **Method:** Content-based hashing (SHA256)
- **Goal:** Eliminate duplicate blocks across nodes
- **Metric:** Dedup ratio = original_blocks / unique_blocks
- **Example:** 8 files → 6 unique blocks (25% saved)

### 2. Distribution & Replication
- **Strategy:** Random block placement to R nodes (default R=2)
- **Effect:** Increases fault tolerance, improves read parallelism
- **Trade-off:** More replicas → more storage, but better availability

### 3. Load Balancing
- **Detection:** Calculate load variance across nodes
- **Trigger:** Variance exceeds threshold (default 1.0)
- **Rebalancing:** Greedy algorithm (most-loaded → least-loaded)
- **Metric:** Variance before/after rebalancing

### 4. Hypergraph Modeling
- **Structure:** NetworkX graph where:
  - Nodes = storage nodes (N1, N2, N3)
  - Edges = shared files between nodes
  - Edge weight = count of shared files
- **Purpose:** Analyze connectivity & data locality

---

## Project Structure

```
HyperPart-DL/
├── main.py                              # Main orchestration pipeline
├── requirements.txt                     # Python dependencies
├── pyproject.toml                       # Package metadata (pip installable)
├── README.md                            # This file
├── .gitignore                           # Git ignore list
│
├── storage/
│   ├── __init__.py
│   └── node_simulation.py               # StorageNode class
│
├── deduplication/
│   ├── __init__.py
│   └── hashing.py                       # SHA256 content hashing
│
├── repartition/
│   ├── __init__.py
│   └── optimizer.py                     # Load balancing logic
│
├── hypergraph/
│   ├── __init__.py
│   └── hypergraph_model.py              # HyperGraphModel (NetworkX)
│
├── analytics/
│   ├── __init__.py
│   ├── metrics.py                       # Metrics computation
│   ├── visualization.py                 # Matplotlib plots
│   └── interactive_dashboard.py         # Plotly interactive charts
│
├── simulation/
│   ├── __init__.py                      # DynamicSimulation class
│   └── run_dynamic_simulation.py        # Multi-step workload runner
│
├── tests/
│   ├── test_hashing.py                  # 5 unit tests
│   ├── test_storage_node.py             # 6 unit tests
│   ├── test_optimizer.py                # 8 unit tests
│   └── test_main.py                     # 1 integration test
│
└── [Generated at runtime]
    ├── utilization.png                  # Node utilization bar chart
    ├── replication_distribution.png     # File replication distribution
    ├── hypergraph.png                   # NetworkX hypergraph visualization
    ├── dashboard.html                   # Interactive Plotly dashboard
    ├── metrics_replication_counts.csv   # Metadata: file → replication count
    ├── metrics_node_counts.csv          # Node ID → unique files
    └── simulation_metrics_history.csv   # Time-series metrics from dynamic sim
```

---

## Running Simulations

### Static Simulation (Main)
Single-shot file distribution and rebalancing:
```bash
python main.py
```

**Output:**
- Console: Node utilizations, variance before/after, hypergraph info
- Charts: `utilization.png`, `replication_distribution.png`, `hypergraph.png`
- Data: `metrics_replication_counts.csv`, `metrics_node_counts.csv`

**Example Output:**
```
Utilizations before rebalancing:
  N1: 5
  N2: 2
  N3: 5
Load variance before: 2.000

Utilizations after rebalancing:
  N1: 4
  N2: 4
  N3: 4
Load variance after: 0.000

Deduplication ratio: 1.333 (8/6)
Space saved: 25.0%

Hypergraph nodes: N1, N2, N3
Hypergraph edges: N1-N2 (1 shared), N1-N3 (3 shared), N2-N3 (1 shared)
```

### Interactive Dashboard
Generate Plotly-based interactive visualizations:
```bash
python run_interactive_dashboard.py
```

**Output:**
- `dashboard.html` (opens in browser)

**Features:**
- Hover tooltips for node utilization and replication stats
- Interactive network graph of storage nodes
- Time-series plots: variance and dedup ratio over simulation steps
- Responsive layout

**Browser Preview:**
Open `dashboard.html` in any modern web browser (Chrome, Firefox, Safari, Edge).
No server required; all visualizations embedded in single HTML file.

### Dynamic Workload Simulation
Multi-step simulation with file add/remove cycles:
```bash
python run_dynamic_simulation.py
```

**Output:**
- Console: Per-step metrics and rebalancing actions
- Data: `simulation_metrics_history.csv` with 5 rows (one per step)

**CSV Columns:**
- `step`: Time step (0-4)
- `variance`: Load variance
- `dedup_ratio`: Deduplication ratio
- `space_saved_ratio`: Percentage of storage saved via dedup

**Example CSV:**
```
step,variance,dedup_ratio,space_saved_ratio
0,0.222,1.000,0.0
1,0.222,1.000,0.0
2,0.222,1.000,0.0
3,0.889,1.000,0.0
4,0.222,1.000,0.0
```

### Heterogeneous Node Capacities

Run a simulation where nodes have different storage capacities:

```bash
python run_hetero_simulation.py
```

This creates `hetero_utilization.png`, `hetero_metrics_node_counts.csv`, and `hetero_metrics_replication_counts.csv`, and `hetero_simulation_history.csv`.

The `DynamicSimulation` constructor accepts an optional `capacities` list (per-node integer capacities) for custom scenarios:

```python
from simulation import DynamicSimulation
sim = DynamicSimulation(num_nodes=3, replication_factor=2, capacities=[5,3,8])
sim.run_simulation(steps=5)
```

The interactive dashboard and CSV exports now include `capacity` and `util_ratio` per node, and time-series charts show active/failed node counts.

---

## Metrics & Outputs

### Key Metrics

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| **Utilization** | blocks_stored / node | % of node capacity used |
| **Load Variance** | var([util_N1, util_N2, util_N3]) | Higher = more imbalanced |
| **Dedup Ratio** | original_blocks / unique_blocks | Higher = more duplicates |
| **Space Saved** | (1 - unique/original) × replication | % of storage that dedup saves |

*** End Patch