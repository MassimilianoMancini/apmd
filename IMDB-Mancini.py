import re
import networkx as nx
import random
from heapq import heapreplace
from numpy import log
from datetime import datetime
from itertools import combinations

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

        # Regular Expression in fast and verbose flavours
        self.reForYear = re.compile('(\()(\d\d\d\d)([/IXV])*(\))')
        self.reActorMovieYear = re.compile('(.+)\t(.+(?<=\()(\d\d\d\d)(?=[/IXV]*\)).*)')

        # Global time for DFS
        self.dfstime = 0

        self.topTenCentralActors = [(0, '')]*10

        self.movies = set()

    def setCli(self, cli):
        self.cli = cli
    
    def generateSample(self, fraction):
        f = open("imdb-actors-actresses-movies.tsv", "r")
        g = open("sample.tsv", "w")
        i = 0
        for line in f:
            lucky = random.randint(0, fraction)
            if (lucky == 13):
                g.write(line)
                i += 1

        f.close
        g.close
        return i

    def getDecade(self, year):
        if year < 1931:
            return 1930
        else:
            return ((year + 9) // 10) * 10
    
    def getValues(self, line, logfile):
        
        failure = '', '', '', True
        actor, movie = line.split('\t')

        if self.mainGraph.has_edge(actor, movie):
            logfile.write('DUPLICATE: ' + line)
            return failure
        
        yearMatched = self.reForYear.search(movie)

        if not yearMatched:
            logfile.write('YEAR NOT FOUND: ' + line)
            return failure
     
        strYear = yearMatched.group(2)
        return actor, movie, int(strYear), False

    def createFromFile(self, path, verbose):
        if verbose:
            self._createFromFileVerbose(path)
        else:
            self._createFromFileFast(path)
     
    def _createFromFileFast(self, path):
        f = open(path, 'r')
        for line in f:
            matchedLine = self.reActorMovieYear.match(line)
            if matchedLine:
                actor = matchedLine.group(1)
                movie = matchedLine.group(2)
                year = int(matchedLine.group(3))
                decade = self.getDecade(year)
                self.addNodeToMainGraph(actor, movie, year)
                self.addNodeToProdGraph(actor, decade)
        f.close

    def _createFromFileVerbose(self, path):
        f = open(path, 'r')
        log = open(self.logFile, 'w')
        i = 1
        for line in f:
            actor, movie, year, failure = self.getValues(line, log)
            if not failure:
                self.addNodeToMainGraph(actor, movie, year)
                self.addNodeToProdGraph(actor, self.getDecade(year))
            self.cli.message(f'Lines read: {i:,}', '\r')
            i += 1
        log.close
        f.close

    def addNodeToMainGraph(self, actor, movie, year):
        self.mainGraph.add_node(actor, type='actor', color='white', dist = 0, totdist = 0, chat = None)
        self.mainGraph.add_node(movie, type='movie', year=year, color='white', dist = 0, totdist = 0, chat = None)
        self.mainGraph.add_edge(actor, movie)
        self.movies.add(movie)

    def addNodeToProdGraph(self, actor, fromDecade):
        for decade in range(fromDecade, self.lastDecade, 10):
            if self.prodGraph.has_edge(decade, actor):
                self.prodGraph.edges[decade, actor]['weight'] += 1
            else:
                self.prodGraph.add_node(actor, type='actor')
                self.prodGraph.add_edge(decade, actor, weight = 1)

    def getMostProductiveActorUntil(self, decade):
        max = 0
        mostProductiveActor = None
        for actor in self.prodGraph[decade]:
            if self.prodGraph.edges[decade, actor]['weight'] > max:
                max = self.prodGraph.edges[decade, actor]['weight']
                mostProductiveActor = actor
        return mostProductiveActor, max
    
    def _getFilteredBiggestCC(self, decade):
        self.cli.notify('Calculating biggest CC start')

        for node in self.mainGraph:
            self.mainGraph.nodes[node]['color'] = 'white'

        maxDimension = 0
        biggestCC = []
        remainNodes = self.mainGraph.number_of_nodes()

        for movie in self.mainGraph:
            dimension = 0
            cc = []
            m = self.mainGraph.nodes[movie]
            if m['type'] == 'movie' and m['year'] <= decade and m['color'] == 'white':
                cc = self._filteredCC(movie, decade)
                dimension = len(cc)
                remainNodes = remainNodes - dimension
                if dimension > maxDimension:
                    maxDimension = dimension
                    biggestCC = cc.copy()
            if maxDimension > remainNodes:
                break

        self.cli.notify(f'The biggest CC is {biggestCC[0]} with {len(biggestCC)} nodes')
        return biggestCC

    def _filteredCC(self, start, decade):
        cc = [start]
        i = 0
        while i < len(cc):
            currentNode = cc[i]
            for nextNode in self.mainGraph[currentNode]:
                nn = self.mainGraph.nodes[nextNode]
                if nn['color'] == 'white' and (nn['type'] == 'actor' or (nn['type'] == 'movie' and nn['year'] <= decade)):
                    nn['color'] = 'gray'
                    cc.append(nextNode)
            i += 1
            self.mainGraph.nodes[currentNode]['color'] = 'black'
        return cc

    def cHat(self, decade, eps):
        cc = self._getFilteredBiggestCC(decade)
        subGraph = self.mainGraph.subgraph(cc)
        n = subGraph.number_of_nodes()
        k = min(int(log(n)/(eps*eps)) + 1, n)
        self.cli.message(f'Need to do {k} BFSs')
        random_nodes = random.sample(list(subGraph.nodes()), k)
        self.calcSoDForNode(subGraph, random_nodes)
        for node in subGraph:
            cHat = (k*(n-1))/(n*subGraph.nodes[node]['totdist'])
            subGraph.nodes[node]['chat'] = cHat
            if subGraph.nodes[node]['type'] == 'actor' and cHat > self.topTenCentralActors[0][0]:
                heapreplace(self.topTenCentralActors, (cHat, node))
                           
    def calcSoDForNode(self, graph, random_nodes):
        i = 0
        
        for node in graph:
            graph.nodes[node]['totdist'] = 0

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
            i += 1
            self.cli.notify(f'BFS n. {i} done')
        return

    def mostSharedMovies(self):
        maxShared = 0
        movieSubGraph = self.mainGraph.subgraph(self.movies)
        for movie1 in movieSubGraph:
            for actor in self.mainGraph[movie1]:
                if self.mainGraph.degree[actor] > maxShared:
                    for movie2 in self.mainGraph[actor]:
                        if self.mainGraph.degree[movie2] > maxShared and movie2 != movie1:
                            nOfSharedActors = len(set(self.mainGraph[movie1]).intersection(set(self.mainGraph[movie2])))
                            if nOfSharedActors > maxShared:
                                maxShared = nOfSharedActors
                                m1 = movie1
                                m2 = movie2
        return m1, m2, maxShared

    def createActorGraph(self):
        topCouple = [0, None, None]   
        i = 0
        for movie in self.movies:
            m = self.mainGraph[movie]
            if len(m) > 1:
                for actor1, actor2 in combinations(m, 2):
                    if self.actorGraph.has_edge(actor1, actor2):
                        self.actorGraph.edges[actor1, actor2]['weight'] += 1
                        if topCouple[0] < self.actorGraph.edges[actor1, actor2]['weight']:
                            topCouple = [self.actorGraph.edges[actor1, actor2]['weight'], actor1, actor2]
                    else:
                        self.actorGraph.add_edge(actor1, actor2, weight = 1)
            i = i + 1
            self.cli.message(f'Movies processed {i:,}', '\r')
        return topCouple

    def clearGraphs(self):
        self.mainGraph.clear()
        self.prodGraph.clear()
        self.actorGraph.clear()


class Cli():
    def __init__(self, G):
        self.G = G

    def notify(self, string):
        print (f'{string} [{datetime.now().time()}]')

    def message(self, string, e='\n'):
        print (string, end=e)

    def importGraph(self):   
        print ('\n')
        print ('-----------------------------------------')
        print ('IMDB Graph project (Massimiliano Mancini)')
        print ('-----------------------------------------')
        f = int (input('Select file to import or generate a new sample \n[1] Full\n[2] Sample\n[3] Test\n[4] Create new sample and exit\n[0] Exit\n-> '))

        if f == 0:
            exit()
        elif f == 1:
            path = 'imdb-actors-actresses-movies.tsv'
        elif f == 2:
            path = 'sample.tsv'
        elif f == 3:
            path = 'test.tsv'
        elif f == 4:
            s = int(input('Sample 1 row every (min 20)\n[50]-> ') or "50")
            rows = self.G.generateSample(s)
            print (f'File sample.tsv generated with {rows} rows')
            exit()

        f = int (input('[1] Fast import\n[2] Verbose import\n[0] Exit\n-> '))
        if f == 0:
            exit()
        elif f == 1:
            verbose = False
            way = 'fast mode'
        elif f ==2:
            verbose = True
            way = 'verbose mode'

        self.notify(f'Import data {way} start (est. 2\')')
        self.G.createFromFile(path, verbose)
        print ('Main graph')
        print (self.G.mainGraph)
        print (f'There are {len(self.G.movies)} movies and {self.G.mainGraph.number_of_nodes() - len(self.G.movies)} actors')
        print ('Producion graph')
        print (self.G.prodGraph)
        self.notify(f'Import data {way} done')

    def mostProductiveActor(self):
        y = int(input('Q1.C: Select decade (1930-2020) for most productive actor\n[2020]->  ') or "2020")

        self.notify(f'Find the most productive actor until {y} start')
        actor, max = self.G.getMostProductiveActorUntil(y)
        print (f'The most productive actor until {y} is {actor} with {max} movies')
        self.notify(f'Find the most productive actor until {y} done')

    def cHat(self):
        y = int(input('Q2.3: Select decade (1930-2020) for biggest connected component\n[2020]-> ') or "2020")
        eps = float(input('Q2.3: Set the epsilon[0.1]\n-> ') or "0.1")
        self.notify(f'Calculate c-hat for all nodes in the biggest CC until year {y} start')
        biggestCC = self.G.cHat(y, eps)
        print ('Most central actors are:')
        for chat, actor in self.G.topTenCentralActors:
            print (f'{actor:30s} \t\t {chat:.5f}')
        self.notify(f'Calculate c-hat for all nodes in the biggest CC until year {y} done')

    def sharingMovies(self):
        self.notify(f'Q3.III Movies that share majority of actors start (est. 3\')')
        m1, m2, n = self.G.mostSharedMovies()
        print (f'The movies that share the majority of actors are {m1} and {m2} with {n} actors in common')
        self.notify(f'Q3.III Movies that share majority of actors done')

    def createActorGraph(self):
        self.notify(f'Q4. Create actor graph start (est. 25\')')
        nOfMovies, actor1, actor2 = self.G.createActorGraph()
        print ('\nActor graph')
        print (self.G.actorGraph)
        print (f'Most shared actors are {actor1} and {actor2} with {nOfMovies} movies')
        self.notify(f'Q4. Create actor graph done')

    def clearGraphs(self):
        self.G.clearGraphs()
        print('All graphes were cleared')

def main():
    G = IMDBGraph()
    cli = Cli(G)
    G.setCli(cli)
    print('\n')
    cli.importGraph()
    print('\n')
    cli.mostProductiveActor()
    print('\n')
    cli.cHat()
    print('\n')
    cli.sharingMovies()
    print('\n')
    cli.createActorGraph()
    print('\n')
    cli.clearGraphs()

if __name__ == "__main__":
    main()
exit()