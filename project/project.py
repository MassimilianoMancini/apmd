import os
import json
import networkx as nx

G = nx.Graph()
for filename in os.listdir("sequences"):
    with open(os.path.join("sequences", filename), 'r') as f:
        nodeName = json.load(f)['query'][3:]
        G.add_node(nodeName)
        print('Added node [%s%%]\r'%nodeName, end="")
print(G)