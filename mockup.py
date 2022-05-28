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
        lastDecade = 2030
        self.prodGraph = nx.Graph()
        for i in range(self.firstDecade, lastDecade, 10):
            self.prodGraph.add_node(i, type="decade")

        # Regular Expression to get year from movie title
        self.reForYear = re.compile("(\()(\d\d\d\d)([/IXV])*(\))")

    def getDecade(self, year):
        if year < 1931:
            return 1930
        elif year < 1941:
            return 1940
        elif year < 1951:
            return 1950
        elif year < 1961:
            return 1960
        elif year < 1971:
            return 1970
        elif year < 1981:
            return 1980
        elif year < 1991:
            return 1990
        elif year < 2001:
            return 2000
        elif year < 2011:
            return 2010
        elif year < 2021:
            return 2020
    
    def getValues(self, line, log):
        
        failure = "", "", "", True
        actor, movie = line.split("\t")

        if self.mainGraph.has_edge(actor, movie):
            log.write("DUPLICATE: " + line)
            return failure
        
        yearMatched = self.reForYear.search(movie)

        if not yearMatched:
            log.write("YEAR NOT FOUND: " + line)
            return failure
     
        strYear = yearMatched.group(2)
        return actor, movie, int(strYear), False
            

    def createFromFile(self):
        f = open(self.path, "r")
        log = open("MovieGraphImportLogger.log", "w")
        message = "Lines read: {:,}"
        lines = f.readlines()
        i = 1
        for line in lines:
            actor, movie, year, failure = self.getValues(line, log)
            if not failure:
                self.addNodeToMainGraph(actor, movie, year)
                # self.addNodeToActorGraph(actor, movie)
                self.addNodeToProdGraph(actor, self.getDecade(year))
            print (message.format(i), end="\r")
            i = i + 1
        log.close
        f.close
        print (" ")

    def addNodeToMainGraph(self, actor, movie, year):
        self.mainGraph.add_node(actor, type="actor")
        self.mainGraph.add_node(movie, type="movie", year=year)
        self.mainGraph.add_edge(actor, movie)

    def addNodeToActorGraph(self, newActor, movie):
        for actor in self.mainGraph[movie]:
            if actor != newActor:
                if self.actorGraph.has_edge(actor, newActor):
                    self.actorGraph.edges[actor, newActor]["weight"] = self.actorGraph.edges[actor, newActor]["weight"] + 1
                else:
                    self.actorGraph.add_edge(actor, newActor, weight = 1)

    def addNodeToProdGraph(self, actor, untilDecade):
        for decade in range(self.firstDecade, untilDecade, 10):
            if self.prodGraph.has_edge(decade, actor):
                weight = self.prodGraph.edges[decade, actor]["weight"]
                self.prodGraph.edges[decade, actor]["weight"] = weight + 1
            else:
                self.prodGraph.add_edge(decade, actor, weight = 1)

    def getMostProductiveActorUntil(self, decade):
        max = 0
        mostProductiveActor = None
        for actor in self.prodGraph[decade]:
            if self.prodGraph.edges[decade, actor]["weight"] > max:
                max = self.prodGraph.edges[decade, actor]["weight"]
                mostProductiveActor = actor
        return mostProductiveActor, max



# START HERE
# path = "imdb-actors-actresses-movies.tsv"
path = "sample.tsv"
G = IMDBGraph(path)

print(datetime.now().time())
G.createFromFile()
print(datetime.now().time())
print (G.mainGraph)
for decade in range (1930, 2030, 10):
    for actor in G.prodGraph[decade]:
        if G.prodGraph.edges[decade, actor]["weight"] > 20:
            print (decade, actor, G.prodGraph.edges[decade, actor]["weight"])


actor, max = G.getMostProductiveActorUntil(1990)
print (actor, max)
print(datetime.now().time())
