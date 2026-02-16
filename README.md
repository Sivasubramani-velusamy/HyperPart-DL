# HyperPart-DL

Lightweight distributed storage simulation with deduplication, load imbalance detection/rebalancing, and hypergraph modeling of replicated files.

Prerequisites
- Python 3.11 (recommended)
- Git (optional)

Quick setup (Windows)
1. Create and activate a Python 3.11 venv:

```
py -3.11 -m venv .venv311
.\.venv311\Scripts\activate
```

2. Upgrade pip and install dependencies:

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run

```
python main.py
```

Outputs
- The script prints node utilizations and hypergraph info to stdout.
- The node utilization plot is saved to `utilization.png` in the project root (non-blocking).

Notes
- If `pip install` fails building packages (e.g. `pandas`) on newer Python releases, ensure you are using Python 3.11 or install Visual Studio build tools. Alternatively remove `pandas` from `requirements.txt` when running on a different interpreter.
- To run fully headless you can set the matplotlib backend before running:

Windows cmd:
```
set MPLBACKEND=Agg&& python main.py
```
PowerShell:
```
$env:MPLBACKEND="Agg"; python main.py
```

Project layout

```
HyperPart-DL/
  main.py
  requirements.txt
  README.md
  dataset/
  storage/node_simulation.py
  deduplication/hashing.py
  repartition/optimizer.py
  hypergraph/hypergraph_model.py
  analytics/visualization.py
```


"# HyperPart-DL" 
