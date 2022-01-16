import os
import json
import networkx as nx

G = nx.Graph()
for filename in os.listdir("sequences"):
    with open(os.path.join("sequences", filename), 'r') as f:
        G.add_node(json.load(f)['query'][-3:])
print(G)