import json
import re
import os
import itertools
import networkx as nx

class OEISJsonFiles:
    def withCommentSection(self, path):
        files = os.listdir(path)
        items = []
        for filename in files:
            with open(os.path.join(path, filename)) as f:
                file = {}
                jsonData = json.load(f)
                file['id'] = jsonData['query'][3:]
                if 'results' in jsonData and 'comment' in jsonData['results'][0]:
                    file['comment'] = jsonData['results'][0]['comment']
                    items.append(file)
        return items

class APMDGraph(nx.Graph):    
    def createFromFiles(self, path):
        authors = {}
        i = 0.0
        j = 1
        G = nx.Graph()
        oeisfiles = OEISJsonFiles()
        files = oeisfiles.withCommentSection(path)
        for file in files:            
            authors = []
            for s in file['comment']:
                x = re.search(r"- _([a-zA-Z., -]+)_", s)
                if x:
                    authors.append(x.group(1))
                        
            if (len(authors) >= 2):
                G.add_edges_from(itertools.combinations(authors, 2), label=file['id'])

g = APMDGraph()
g.createFromFiles('sequences')

print(g)
