import json
import re
import os
import itertools
import networkx as nx

authors = {}
i = 0.0
j = 1
G = nx.Graph()
print ("Import data from files")
print ("0%", end="")

for filename in os.listdir('sequences'):
    i = i + (1/832)
    if (i > j and j <= 100):
        print (".", end="")
        j = j + 1
        if (j % 10 == 0):
            print (f"{j}%", end="")
    
    f = open(os.path.join('sequences', filename), 'r')
    data = json.load(f)
    nodeName = data['query'][3:]
    if 'results' in data and 'comment' in data['results'][0]:
        for s in data['results'][0]['comment']:
            x = re.search(r"- _([a-zA-Z., -]+)_", s)
            if x:
                author = x.group(1)
                if author in authors:
                    if nodeName not in authors[author]:
                        authors[author].append(nodeName)
                else:
                    authors[author] = [nodeName]

    G.add_node(nodeName)
    f.close()

print("\nData imported. Creating graph...")

for author in authors:
    G.add_edges_from(itertools.combinations(authors.get(author), 2))
    
print(G)

