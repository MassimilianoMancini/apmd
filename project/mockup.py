import logging
import re
import networkx as nx

class IMDBGraph():
    def __init__(self, path):
        self.graph = nx.Graph()
        self.path = path
        # Regular Expression
        # will work on movie part of string 
        # first group an opening parenthesis
        # second group the year (4 digits)
        # third optional group slash with roman numbers
        # four group a closing parenthesis
        self.reForYear = re.compile("(\()(\d\d\d\d)([/IXV])*(\))")
        self.actorSubGraph = {}
        self.movieSubGraph = {}
        


    def logProblems(self):
        log = open("project/MovieGraphImportLogger.log", "w")
        G = nx.Graph()

        f = open(self.path, "r")
        lines = f.readlines()
        for line in lines:
            actor, movie = line.split("\t")
            if G.has_edge(actor, movie):
                log.write("DUPLICATE: " + actor +  ":" +  movie)
            else:
                G.add_edge(actor, movie)
                # Check for yar problem only if edge does not exist
                # This way number of lines of log file
                # and nodes will be consistent
                # |G| = lines of input file - errors
                # 8.104.335 - 855 = 8.103.480
                if not self.reForYear.search(movie):
                    log.write("NO YEAR: " + actor +  ":" +  movie)
        f.close
        log.close

    def createFromFile(self):
        f = open(self.path, "r")
        lines = f.readlines()
        for line in lines:
            actor, movie = line.split("\t")
            y = self.reForYear.search(movie)
            #discard not matching string, e.g. lines without year see Aamundson
            if y:
                # get second group, 4 digits i.e. the year
                year = y.group(2)
                self.graph.add_node(actor, type="actor")
                self.graph.add_node(movie, type="movie", year=int(year))
                self.graph.add_edge(actor, movie)
        self.actorSubGraph = {n for n, d in self.graph.nodes(data=True) if d['type'] == 'actor'}
        self.movieSubGraph = {n for n, d in self.graph.nodes(data=True) if d['type'] == 'movie'}
        f.close
    
    def mostActiveActorUntil(self, year):
        maxUntilNow = 0
        mostActiveActor = ""
        for actor in self.actorSubGraph:
            if self.graph.degree(actor) > maxUntilNow:
                i = sum(1 for m in self.graph[actor] if nx.get_node_attributes(self.graph, 'year')[m] <= year)
                maxUntilNow = max(maxUntilNow, i)
            mostActiveActor = actor
        return mostActiveActor

# START HERE
path = "project/test.tsv"
G = IMDBGraph(path)
# You could split into two sections: first find problems, second fast create consistent graph
# G.logProblems()
# print ("Problems found")
# Create graph after problems were found
G.createFromFile()
print (G.graph)
a = G.mostActiveActorUntil(1980)
print(a)