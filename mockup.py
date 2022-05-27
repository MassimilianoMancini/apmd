import logging
import re
import networkx as nx
from datetime import datetime

class IMDBGraph():
    def __init__(self, path):

        # Import tsv file path
        self.path = path

        # Main graph as requested for basic project
        self.mainGraph = nx.Graph()
        
        # Actor graph as requesto for question 4
        self.actorGraph = nx.Graph()

        # Most productive actor in last decades for question 1.C
        self.firstDecade = 1930
        lastDecade = 2020
        self.prodGraph = nx.Graph()
        for i in range(self.firstDecade, lastDecade, 10):
            self.prodGraph.add_node(i, type="decade")

        # Regular Expression to get year from movie title
        self.reForYear = re.compile("(\()(\d\d\d\d)([/IXV])*(\))")

    def getDecade(year):
        return (year % 10) * 10

    def createFromFile(self):
        f = open(self.path, "r")
        log = open("MovieGraphImportLogger.log", "w")
        lines = f.readlines()
        for line in lines:
            actor, movie = line.split("\t")
            if self.mainGraph.has_edge(actor, movie):
                log.write("DUPLICATE: " + actor +  ":" +  movie)
            else:
                y = self.reForYear.search(movie)
                #discard lines without year (e.g. Aamundson)
                if y:
                    year = y.group(2)

                    self.addNodeToMainGraph(actor, movie, year)
                    self.addNodeToActorGraph(actor, movie)
                    self.addNodeToProdGraph(actor, movie, self.getDecade(year))

                else:
                    log.write("NO YEAR: " + actor +  ":" +  movie)
        log.close
        f.close

    def addNodeToMainGraph(self, actor, movie, year):
        self.mainGraph.add_node(actor, type="actor")
        self.mainGraph.add_node(movie, type="movie", year=int(year))
        self.mainGraph.add_edge(actor, movie)

    def addNodeToActorGraph(self, newActor, movie):
        for actor in self.mainGraph[movie].items():
            self.actorGraph.add_edge(actor, newActor)

    def addNodeToProdGraph(self, actor, decade):
        for d in range(self.firstDecade, decade, 10):
            if self.prodGraph.has_edge(decade, actor):
                self.prodGraph[d, actor]["weight"] = self.prodGraph[d, actor]["weight"] + 1
            else:
                self.prodGraph.add_edge(d, actor, weight=1)




    
    def mostActiveActorUntil(self, year):
        maxUntilNow = 0
        mostActiveActor = ""
        for actor in self.actorSubGraph:
            if self.graph.degree(actor) > maxUntilNow:
                i = sum(1 for m in self.graph[actor] if nx.get_node_attributes(self.graph, 'year')[m] <= year)
                if i > maxUntilNow:
                    maxUntilNow = i
                    mostActiveActor = actor
        return mostActiveActor

# START HERE
path = "imdb-actors-actresses-movies.tsv"
G = IMDBGraph(path)
# You could split into two sections: first find problems, second fast create consistent graph
# G.logProblems()
# print ("Problems found")
# Create graph after problems were found
print(datetime.now().time())
G.createFromFile()
print(datetime.now().time())
print (G.graph)
print(datetime.now().time())
a = G.mostActiveActorUntil(2010)
print(datetime.now().time())
print(a)