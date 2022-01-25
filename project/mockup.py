import json
import re
import os
import itertools
import networkx as nx
import logging

class APMDGraph(nx.Graph):

    resultSection = ''
    commentSection = ''
    querySection = ''

    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        self.resultSection = 'result'
        self.commentSection = 'comment'
        self.querySection = 'query'
    
    def createFromFiles(self, path):

        logging.basicConfig(filename='import.log', encoding='utf-8', level=logging.DEBUG)


        authors = {}
        i = 0.0
        j = 1
        G = nx.Graph()
        print ("Import data from files")
        print ("0%", end="")

        for filename in os.listdir(path):
            i = i + (1/832)
            if (i > j and j <= 100):
                print (".", end="")
                j = j + 1
                if (j % 10 == 0):
                    print (f"{j}%", end="")
            
            with open(os.path.join(path, filename), 'r') as f:
                data = json.load(f)
                nodeName = data[self.querySection][3:]
                if 'results' in data and 'comment' in data['results'][0]:
                    authors = []
                    for s in data['results'][0]['comment']:
                        x = re.search(r"- _([a-zA-Z., -]+)_", s)
                        if x:
                            authors.append(x.group(1))
                        
                    if (len(authors) < 2):
                        logging.info(f"file {nodeName} does not have enough authors")
                    else:
                        G.add_edges_from(itertools.combinations(authors, 2), label=nodeName)

                else:
                    logging.info(f"file {nodeName} does not have comment section")
print ("\n")
print(G)
print ("\n")
print(G.nodes)
print ("\n")
print(G.edges(data=True))

