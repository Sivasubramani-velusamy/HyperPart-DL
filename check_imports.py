import importlib
mods = ['storage.node_simulation','repartition.optimizer','hypergraph.hypergraph_model','analytics.metrics','analytics.interactive_dashboard']
for m in mods:
    try:
        importlib.import_module(m)
        print('OK', m)
    except Exception as e:
        print('ERR', m, e)
