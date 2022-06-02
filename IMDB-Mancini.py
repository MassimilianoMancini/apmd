import logging
import re
import networkx as nx
import random
from numpy import log
from datetime import datetime

class IMDBGraph():
    def __init__(self):

        # Log File for error in verbose mode
        self.logFile = 'MovieGraphImportLogger.log'

        # Main graph as requested for basic project
        self.mainGraph = nx.Graph()
        
        # Actor graph as requesto for question 4
        self.actorGraph = nx.Graph()

        # Most productive actor in last decades for question 1.C
        self.firstDecade = 1930
        self.lastDecade = 2030
        self.prodGraph = nx.Graph()
        for i in range(self.firstDecade, self.lastDecade, 10):
            self.prodGraph.add_node(i, type='decade')

        # Regular Expression in verbose and fast flavours
        self.reForYear = re.compile('(\()(\d\d\d\d)([/IXV])*(\))')
        self.reActorMovieYear = re.compile('(.+)\t(.+(?<=\()(\d\d\d\d)(?=[/IXV]*\)).*)')

        # Global time for DFS
        self.dfstime = 0

        self.topTenCentralActors = [[0, '']]*10

    def generateSample(self, fraction = 50):
        f = open("imdb-actors-actresses-movies.tsv", "r")
        g = open("sample.tsv", "w")
        i = 0
        for line in f:
            lucky = random.randint(0, fraction)
            if (lucky == 13):
                g.write(line)
                i = i + 1

        f.close
        g.close
        return i

    def getDecade(self, year):
        if year < 1931:
            return 1930
        else:
            return ((year + 9) // 10) * 10
    
    def getValues(self, line, log):
        
        failure = '', '', '', True
        actor, movie = line.split('\t')

        if self.mainGraph.has_edge(actor, movie):
            log.write('DUPLICATE: ' + line)
            return failure
        
        yearMatched = self.reForYear.search(movie)

        if not yearMatched:
            log.write('YEAR NOT FOUND: ' + line)
            return failure
     
        strYear = yearMatched.group(2)
        return actor, movie, int(strYear), False

    def createFromFile(self, path, verbose=False):
        if verbose:
            self._createFromFileVerbose(path)
        else:
            self._createFromFileFast(path)
     
    def _createFromFileFast(self, path):
        f = open(path, 'r')
        # lines = f.readlines()
        for line in f:
            matchedLine = self.reActorMovieYear.match(line)
            if matchedLine:
                actor = matchedLine.group(1)
                movie = matchedLine.group(2)
                year = int(matchedLine.group(3))
                decade = self.getDecade(year)
                self.addNodeToMainGraph(actor, movie, year)
                # self.addNodeToActorGraph(actor, movie, decade)
                self.addNodeToProdGraph(actor, decade)
        f.close

    def _createFromFileVerbose(self, path):
        f = open(path, 'r')
        log = open(self.logFile, 'w')
        message = 'Lines read: {:,}'
        lines = f.readlines()
        i = 1
        for line in lines:
            actor, movie, year, failure = self.getValues(line, log)
            if not failure:
                self.addNodeToMainGraph(actor, movie, year)
                self.addNodeToActorGraph(actor, movie)
                self.addNodeToProdGraph(actor, self.getDecade(year))
            print (message.format(i), end='\r')
            i = i + 1
        log.close
        f.close
        print (' ')

    def addNodeToMainGraph(self, actor, movie, year):
        self.mainGraph.add_node(actor, type='actor', color='white', dist = 0, totdist = 0, chat = None)
        self.mainGraph.add_node(movie, type='movie', year=year, color='white', dist = 0, totdist = 0, chat = None)
        self.mainGraph.add_edge(actor, movie)

    def addNodeToActorGraph(self, newActor, movie):
        for actor in self.mainGraph[movie]:
            if actor != newActor:
                if self.actorGraph.has_edge(actor, newActor):
                    self.actorGraph.edges[actor, newActor]['weight'] = self.actorGraph.edges[actor, newActor]['weight'] + 1
                else:
                    self.actorGraph.add_edge(actor, newActor, weight = 1)

    def addNodeToProdGraph(self, actor, fromDecade):
        for decade in range(fromDecade, self.lastDecade, 10):
            if self.prodGraph.has_edge(decade, actor):
                weight = self.prodGraph.edges[decade, actor]['weight']
                self.prodGraph.edges[decade, actor]['weight'] = weight + 1
            else:
                self.prodGraph.add_node(actor, type='actor')
                self.prodGraph.add_edge(decade, actor, weight = 1)

    def getMostProductiveActorUntil(self, decade = 2020):
        max = 0
        mostProductiveActor = None
        for actor in self.prodGraph[decade]:
            if self.prodGraph.edges[decade, actor]['weight'] > max:
                max = self.prodGraph.edges[decade, actor]['weight']
                mostProductiveActor = actor
        return mostProductiveActor, max
    
    def _getFilteredBiggestCC(self, year = None):
        if year == None:
            year = self.lastDecade

        for node in self.mainGraph:
            self.mainGraph.nodes[node]['color'] = 'white'

        maxDimension = 0
        biggestCC = []
        remainNodes = self.mainGraph.number_of_nodes()

        for movie in self.mainGraph:
            dimension = 0
            cc = []
            m = self.mainGraph.nodes[movie]
            if m['type'] == 'movie' and m['year'] <= year and m['color'] == 'white':
                cc = self._filteredCC(movie, year)
                dimension = len(cc)
                remainNodes = remainNodes - dimension
                if dimension > maxDimension:
                    maxDimension = dimension
                    biggestCC = cc.copy()
            if maxDimension > remainNodes:
                break   
        return biggestCC

    def _filteredCC(self, start, year):
        cc = [start]
        i = 0
        while i < len(cc):
            currentNode = cc[i]
            for nextNode in self.mainGraph[currentNode]:
                nn = self.mainGraph.nodes[nextNode]
                if nn['color'] == 'white' and (nn['type'] == 'actor' or (nn['type'] == 'movie' and nn['year'] <= year)):
                    nn['color'] = 'gray'
                    cc.append(nextNode)
            i = i + 1
            self.mainGraph.nodes[currentNode]['color'] = 'black'
        return cc

    def cHat(self, year, eps):
        cc = self._getFilteredBiggestCC(year)
        subGraph = self.mainGraph.subgraph(cc)
        n = subGraph.number_of_nodes()
        k = min(int(log(n)/eps) + 1, n)
        print (f'Need to do {k} BFSs')
        random_nodes = set(random.sample(list(subGraph.nodes()), k))
        self.calcSoDForNode(subGraph, random_nodes)
        for node in subGraph:
            cHat = (k*(n-1))/(n*subGraph.nodes[node]['totdist'])
            subGraph.nodes[node]['chat'] = cHat
            if subGraph.nodes[node]['type'] == 'actor':
                self._updateTopTenCentralActors(cHat, node)
            
    
    def _updateTopTenCentralActors(self, cHat, node):
        if cHat > self.topTenCentralActors[-1][0]:
                self.topTenCentralActors[-1] = [cHat, node]
                self.topTenCentralActors.sort(reverse=True)
            
    def calcSoDForNode(self, graph, random_nodes):
        for node in graph:
            graph.nodes[node]['totdist'] = 0
        i = 0
        for v in random_nodes:
            for node in graph:
                graph.nodes[node]['color'] = 'white'
                graph.nodes[node]['dist'] = 0

            queue = [v]
            
            while len(queue):
                current = queue.pop()
                for nbr in graph[current]:
                    nn = graph.nodes[nbr]
                    if nn['color'] == 'white':
                        nn['color'] = 'gray'
                        nn['dist'] = graph.nodes[current]['dist'] + 1
                        nn['totdist'] += nn['dist']
                        queue.append(nbr)
                graph.nodes[current]['color'] = 'black'
            i = i + 1
            print (f'BFS n. {i} done')
            print(datetime.now().time())
        return

def main(): 

    G = IMDBGraph()    
    print ('\n')
    print ('-----------------------------------------')
    print ('IMDB Graph project (Massimiliano Mancini)')
    print ('-----------------------------------------')
    f = int (input('Select file to import or generate a new sample [1]Full, [2]Sample [3]Test, [4]New sample (and exit), [0]Exit: '))

    if f == 0:
        exit()
    elif f == 1:
        path = 'imdb-actors-actresses-movies.tsv'
    elif f == 2:
        path = 'sample.tsv'
    elif f == 3:
        path = 'test.tsv'
    elif f == 4:
        s = int(input('Sample 1 row every [50] (min 20): ') or "50")
        rows = G.generateSample(s)
        print (f'File sample.tsv generated with {rows} rows')
        exit()

    f = int (input('[1]Fast import, [2]Verbose import, [0]Exit: '))
    if f == 0:
        exit()
    elif f == 1:
        verbose = False
        way = 'fast mode'
    elif f ==2:
        verbose = True
        way = 'verbose mode'

    print (f'Import data {way}: start')
    print(datetime.now().time())
    G.createFromFile(path, verbose)
    print(datetime.now().time())
    print (f'Import data {way}: done')

    print ('Main graph')
    print (G.mainGraph)

    print ('Producion graph')
    print (G.prodGraph)

    print ('\n')

    y = int(input('Q1.C: Select decade (1930-2020) for most productive actor[2020]: ') or "2020")

    print (f'Find the most productive actor until {y}: start')
    print(datetime.now().time())
    actor, max = G.getMostProductiveActorUntil(y)
    print(datetime.now().time())
    print (f'Find the most productive actor until {y}: done')
    print (f'The most productive actor until {y} is {actor} with {max} movies')

    print ('\n')

    y = int(input('Q2.3: Select decade (1930-2020) for biggest connected component[2020]: ') or "2020")
    eps = float(input('Q2.3: Set the epsilon[0.1]: ') or "0.1")

    print ('\n')
    print (f'Calculate c-hat for all nodes in the biggest CC, year {y}')
    print (datetime.now().time())
    biggestCC = G.cHat(y, eps)
    print (datetime.now().time())
    print ('\n')
    print ('Most central actors are:')
    for chat, actor in G.topTenCentralActors:
        print (f'{actor:>20} \t\t {chat:.5f}')

    exit()

if __name__ == "__main__":
    main()