import re
import os
import itertools
import networkx as nx

class ViewProgress:
    def __init__(self, t):
        self.t = t
        self.i = 0.0
        self.j = 1
        print ("Import data from IMDB file")
        print ("0%", end="")

    def update(self):
        self.i = self.i + (100/self.t)
        if (self.i > self.j and self.j <= 100):
            print (".", end="")
            self.j = self.j + 1
            if (self.j % 10 == 0):
                print (f"{self.j}%", end="")

        if (self.i == self.t): 
            print (f"{self.i} tsv file imported")
        
class IMDBFile:
    with open(os.path.join(path, filename)) as f:
        file = {}
        file['id'] = jsonData['query'][3:]
        if 'results' in jsonData and 'comment' in jsonData['results'][0]:
            file['comment'] = jsonData['results'][0]['comment']
            items.append(file)
        vp.update()
    return items

class APMDGraph(nx.Graph):    
    def createFromFiles(self, path):
        authors = {}
        i = 0.0
        j = 1
        oeisfiles = OEISJsonFiles()
        files = oeisfiles.withCommentSection(path)
        for file in files:            
            authors = []
            for s in file['comment']:
                x = re.search(r"- _([a-zA-Z., -]+)_", s)
                if x:
                    authors.append(x.group(1))
                        
            if (len(authors) >= 2):
                self.add_edges_from(itertools.combinations(authors, 2), label=file['id'])

g = APMDGraph()
g.createFromFiles('sequences')

print(g)
