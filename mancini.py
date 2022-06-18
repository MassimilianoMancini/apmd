import re
import networkx as nx
import random
import os
import gc
from heapq import heapreplace
from math import log
from datetime import datetime


class IMDBGraph():
    """
    Graphs are: main, production and actor.
    Methods for import data from file, calculate connected components, BFS 
    and closeness centrality approximation are implemented
    """

    def __init__(self):

        # Log File for error in verbose mode
        self.logFile = 'MovieGraphImportLogger.log'

        # Main graph as requested for basic project
        self.mainGraph = nx.Graph()
        
        # Actor graph as requested for question 4
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

        # Structure to record top ten actor wrt closeness centrality approx
        self.topTenCentralActors = [(0, '')]*10

        # Set with movie titles
        self.movies = set()

        # Set with actor names
        self.actors = set()
  
    def setCli(self, cli):
        """
        Set cli interface to send notification messages
        """
        self.cli = cli
    
    def generateSample(self, fraction):
        """
        Generate a sample input file from original complete file
        sampling one row out of fraction
        """
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
        """
        Return decade in range 1930 - 2020 given year
        """
        if year < 1931:
            return 1930
        else:
            return ((year + 9) // 10) * 10
    
    def getValues(self, line, logfile):
        """
        Retrieve values of actor, movie and year from a line of input file.
        Also log errors of duplicated line or missing year in a log file. 
        """
        
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
        """
        Exposed method to let user choose fast or verbose mode of import
        """
        if verbose:
            self._createFromFileVerbose(path)
        else:
            self._createFromFileFast(path)
        
    def _createFromFileFast(self, path):
        """
        Create main graph and production graph from input file in a fast way. 
        This means that all read errors are discarded without notification 
        and no progress messages are displayed. In order to log errors and 
        have progress message use verbose way
        """
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
        """
        Create main graph and production graph from input file in verbose way. 
        This means that all errors are logged and a progress message is 
        displayed during import. Verbose time is about twice as long as fast way
        """
        f = open(path, 'r')
        log = open(self.logFile, 'w')
        i = 1
        for line in f:
            actor, movie, year, failure = self.getValues(line, log)
            if not failure:
                decade = self.getDecade(year)
                self.addNodeToMainGraph(actor, movie, year)
                self.addNodeToProdGraph(actor, decade)
            self.cli.message(f'Lines read: {i:,}', '\r')
            i += 1
        log.close
        f.close

    def addNodeToMainGraph(self, actor, movie, movieYear):
        """
        Add a single node to main graph. Default attributes on node are setted.
        It also feed the list of movies that will be used in other methods
        """
        self.mainGraph.add_node(actor, type='actor', color='white', dist = 0, totdist = 0, chat = None)
        self.mainGraph.add_node(movie, type='movie', year=movieYear, color='white', dist = 0, totdist = 0, chat = None)
        self.mainGraph.add_edge(actor, movie)
        self.movies.add(movie)
        self.actors.add(actor)

    def addNodeToProdGraph(self, actor, fromDecade):
        """
        Add a single node to production graph.
        Production graph is used to count the most productive actor within 
        a defined decade. Production graph is a bipartite graph with two types
        of nodes: decade and actor. A weigted edge connect an actor to a decade
        counting the number of movies that the actor have done within that decade
        """
        for decade in range(fromDecade, self.lastDecade, 10):
            if self.prodGraph.has_edge(decade, actor):
                self.prodGraph.edges[decade, actor]['weight'] += 1
            else:
                self.prodGraph.add_edge(decade, actor, weight = 1)

    def getMostProductiveActorUntil(self, decade):
        """
        Return the most productive actor within a defined decade.
        Just iter on decades nodes and retrieve the heaviest edge
        """
        max = 0
        mostProductiveActor = None
        for actor in self.prodGraph[decade]:
            if self.prodGraph.edges[decade, actor]['weight'] > max:
                max = self.prodGraph.edges[decade, actor]['weight']
                mostProductiveActor = actor
        return mostProductiveActor, max
    
    def cHat(self, decade, eps):
        """
        Calculates approximated closeness centrality (c-hat) for all nodes of
        main graph. Approximation is achieved doing k BFSs from different
        k vertexes randomly sampled. If k is in the order of theta log(n)/eps^2
        than the stimator is proven to be correct
        In order to retrieve the top 10 most central actor, a heap data
        structure (heapq) is used. 
        """
        cc = self._getFilteredBiggestCC(decade)
        subGraph = self.mainGraph.subgraph(cc)
        n = subGraph.number_of_nodes()
        k = min(int(log(n)/(eps*eps)) + 1, n)
        self.cli.message(f'Need to do {k} BFSs')
        random_nodes = random.sample(list(subGraph.nodes()), k)
        self._calcSoDForNode(subGraph, random_nodes)
        for node, data in subGraph.nodes.data():
            cHat = (k*(n-1))/(n*(max(data['totdist'],1)))
            data['chat'] = cHat
            if data['type'] == 'actor' and cHat > self.topTenCentralActors[0][0]:
                heapreplace(self.topTenCentralActors, (cHat, node))

    def _getFilteredBiggestCC(self, decade):
        """
        Returns the biggest connected component filtered by year
        (or in this project by decade). It is realized through 
        a BFS (_filteredCC) that filter movie nodes by year. 
        Main loop exits if remaining nodes are less or equal 
        then nodes in CC. In case of two CC with same degree, 
        the first discovered is taken
        """
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
            if maxDimension >= remainNodes:
                break

        self.cli.notify(f'The biggest CC is {biggestCC[0]} with {len(biggestCC)} nodes')
        return biggestCC

    def _filteredCC(self, start, decade):
        """
        Return a list of a filtered CC based on year (or decade in this project)
        A BFS is performed. It uses a queue 
        but elements are not popped out in order to maintain 
        the list of nodes belonging to the connected component
        """
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

                           
    def _calcSoDForNode(self, graph, random_nodes):
        """
        Calculates the sum of distances for every node from a sample of
        random nodes. The sum it is used to calculate the stimated closeness 
        centrality. The sum is stored in totdist attribute
        """
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

    def mostSharedMovies(self):
        """
        Returns the couple of movie that share the biggest number of actors.
        First outer iteration is on movies of graph (movie1), the second iteration 
        is on actors of movie1, the third iteration is again on movies (movie2)
        of actor. This way we find all movies of distance 2. We get cardinality
        of intersection between the two movies and save the maximum
        """

        m2mGraph = nx.Graph()
        maxShared = 0
        for movie1 in self.movies:     
            if self.mainGraph.degree[movie1] > maxShared:
                for actor in self.mainGraph[movie1]:
                    if self.mainGraph.degree[actor] > 1:
                        for movie2 in self.mainGraph[actor]:
                            if (self.mainGraph.degree[movie2] > maxShared) and (movie2 != movie1) and (not m2mGraph.has_edge(movie1, movie2)):
                                m2mGraph.add_edge(movie1, movie2)
                                nOfSharedActors = len(set(self.mainGraph[movie1]).intersection(set(self.mainGraph[movie2])))
                                if nOfSharedActors > maxShared:
                                    maxShared = nOfSharedActors
                                    m1 = movie1
                                    m2 = movie2
        
        m2mGraph.clear()
        return m1, m2, maxShared

    def mostSharedActors(self):
        """
        Returns the couple of actors that share the biggest number of movies.
        First outer iteration is on actors of graph (actor1), the second iteration 
        is on movies of actor1, the third iteration is again on actors (actor2)
        of movie. This way we find all actors of distance 2. We get cardinality
        of intersection between the two actors and save the maximum
        """

        a2aGraph = nx.Graph()
        maxShared = 0
        for actor1 in self.actors:     
            if self.mainGraph.degree[actor1] > maxShared:
                for movie in self.mainGraph[actor1]:
                    if self.mainGraph.degree[movie] > 1:
                        for actor2 in self.mainGraph[movie]:
                            if (self.mainGraph.degree[actor2] > maxShared) and (actor2 != actor1) and (not a2aGraph.has_edge(actor1, actor2)):
                                a2aGraph.add_edge(actor1, actor2)
                                nOfSharedMovies = len(set(self.mainGraph[actor1]).intersection(set(self.mainGraph[actor2])))
                                if nOfSharedMovies > maxShared:
                                    maxShared = nOfSharedMovies
                                    a1 = actor1
                                    a2 = actor2
        
        a2aGraph.clear()
        return a1, a2, maxShared


    def createActorGraph(self):
        """
        Create the actor graph with weighted edges between actors. The weight of
        edges represents the number of movies the two actors did toghether. 
        The main iteration is on movie. For each we create as many edges as 
        the combinations of actors in the movie. If a edge already exists, its
        weght is incremented
        """
        i = 0
        md = len(self.movies)
        for movie in self.movies:
            if len(self.mainGraph[movie]) > 1:
                actorList = list(self.mainGraph.neighbors(movie))
                for idx1 in range(len(actorList) - 1):
                    for idx2 in range(idx1+1, len(actorList)):
                        self.actorGraph.add_edge(actorList[idx1], actorList[idx2])
            i = i + 1
            self.cli.message(f'Movies processed {i:,} on {md:,}', '\r')

class Cli():
    """
    Command line interface, used to get some input and display some output
    """
    def __init__(self, G):
        self.G = G

    def notify(self, string):
        """
        Notify some event with timestamp
        """
        print (f'[{datetime.now().time()}] {string}')

    def message(self, string, e='\n'):
        """
        Print some message, mostly used to display progression
        """
        print (string, end=e)

    def importGraph(self):
        """
        Import graph cli
        """
        print ('\n')
        print ('-----------------------------------------')
        print ('IMDB Graph project (Massimiliano Mancini)')
        print ('-----------------------------------------')
        f1 = int (input('Select file to import or generate a new sample \n[1] Full IMDB archive\n[2] Sample\n[3] Create new sample and exit\n[0] Exit\n-> '))

        if f1 == 0:
            exit()
        elif f1 == 1:
            path = 'imdb-actors-actresses-movies.tsv'
        elif f1 == 2:
            path = 'sample.tsv'
        elif f1 == 3:
            s = int(input('Sample 1 row every (min 20)\n[50]-> ') or "50")
            rows = self.G.generateSample(s)
            print (f'File sample.tsv generated with {rows} rows')
            exit()

        f2 = int (input('[1] Fast import\n[2] Verbose import\n[0] Exit\n-> '))
        if f2 == 0:
            exit()
        elif f2 == 1:
            verbose = False
            way = 'fast mode'
        elif f2 ==2:
            verbose = True
            way = 'verbose mode'
   
            
        self.notify(f'Import data {way} start (est. 2-4\' with full DB)')
        self.G.createFromFile(path, verbose)
        print ('Main graph')
        print (self.G.mainGraph)
        print (f'There are {len(self.G.movies)} movies and {self.G.mainGraph.number_of_nodes() - len(self.G.movies)} actors')
        print ('Producion graph')
        print (self.G.prodGraph)
        self.notify(f'Import data {way} done')

    def mostProductiveActor(self):
        """
        Question 1.C, show the most productive actor until given decade
        """
        y = int(input('Q1.C: Select decade (1930-2020) for most productive actor\n[2020]->  ') or "2020")

        self.notify(f'Find the most productive actor until {y} start')
        actor, max = self.G.getMostProductiveActorUntil(y)
        print (f'The most productive actor until {y} is {actor} with {max} movies')
        self.notify(f'Find the most productive actor until {y} done')

    def cHat(self):
        """
        Question 2.3, calculate approximate closeness centrality for every
        node and show the top ten central actors
        """
        y = int(input('Q2.3: Select decade (1930-2020) for biggest connected component\n[2020]-> ') or "2020")
        eps = float(input('Q2.3: Set the epsilon\n[0.1]-> ') or "0.1")
        self.notify(f'Calculate c-hat for all nodes in the biggest CC until year {y} start')
        self.G.cHat(y, eps)
        print ('Most central actors are:')
        for chat, actor in sorted(self.G.topTenCentralActors, reverse=True):
            print (f'{actor:30s} \t{chat:.5f}')
        self.notify(f'Calculate c-hat for all nodes in the biggest CC until year {y} done')

    def sharingMovies(self):
        """
        Question 3.III, show the movies that have the biggest number of
        actors in common
        """
        self.notify(f'Q3.III Movies that share majority of actors start')
        m1, m2, n = self.G.mostSharedMovies()
        print (f'The movies that share the majority of actors are {m1} and {m2} with {n} actors in common')
        self.notify(f'Q3.III Movies that share majority of actors done')

    def createActorGraph(self):
        """
        Question 4, create the actor graph and show the two actors that 
        partecipate togheter to the biggest number of movies
        """
        self.notify(f'Q4. Create actor graph start (est. 8\' with full DB)')
        actor1, actor2, nOfMovies = self.G.mostSharedActors()
        self.G.createActorGraph()
        print ('\nActor graph')
        print (self.G.actorGraph) 
        print (f'Most shared actors are {actor1} and {actor2} with {nOfMovies} movies')
        self.notify(f'Q4. Create actor graph done')

def main():
    gc.disable()
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
    os._exit(0)

if __name__ == "__main__":
    main()