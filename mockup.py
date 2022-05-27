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
    
    def getValues(self, line, log):
        
        failure = ("", "", "", True)
        actor, movie = line.split("\t")
        if self.mainGraph.has_edge(actor, movie):
            log.write("DUPLICATE: " + line)
            return failure
        
        yearMatched = self.reForYear.search(movie)

        if yearMatched:
            strYear = yearMatched.group(2)
            if strYear.isdigit():
                return (actor, movie, int(strYear), False)
            else:
                log.write("YEAR FORMAT: " + line)
                return failure
        else:
            log.write("YEAR NOT FOUND: " + line)
            return failure


    def createFromFile(self):
        f = open(self.path, "r")
        log = open("MovieGraphImportLogger.log", "w")
        lines = f.readlines()
        for line in lines:
            (actor, movie, year, failure) = self.getValues(line, log)
            if not failure:
                self.addNodeToMainGraph(actor, movie, year)
                self.addNodeToActorGraph(actor, movie)
                self.addNodeToProdGraph(actor, movie, self.getDecade(year))
        log.close
        f.close

    def addNodeToMainGraph(self, actor, movie, year):
        self.mainGraph.add_node(actor, type="actor")
        self.mainGraph.add_node(movie, type="movie", year=int(year))
        self.mainGraph.add_edge(actor, movie)

    def addNodeToActorGraph(self, newActor, movie):
        for actor in self.mainGraph[movie].items():
            self.actorGraph.add_edge(actor, newActor)

    def addNodeToProdGraph(self, actor, untilDecade):
        for decade in range(self.firstDecade, untilDecade, 10):
            if self.prodGraph.has_edge(decade, actor):
                self.prodGraph[decade, actor]["weight"] = self.prodGraph[decade, actor]["weight"] + 1
            else:
                self.prodGraph.add_edge(decade, actor, weight=1)

    def addNodeToProdGraph(self, actor, movie, year):
        pass


# START HERE
path = "imdb-actors-actresses-movies.tsv"
G = IMDBGraph(path)

print(datetime.now().time())
G.createFromFile()
print(datetime.now().time())
print (G.graph)
print(datetime.now().time())
a = G.mostActiveActorUntil(2010)
print(datetime.now().time())
print(a)