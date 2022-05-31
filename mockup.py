import logging
import re
import networkx as nx
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
        self.mainGraph.add_node(actor, type='actor', color='white', discovery = 0, finish = 0, pred = -1)
        self.mainGraph.add_node(movie, type='movie', year=year, color='white', discovery = 0, finish = 0, pred = -1)
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

    def getMostProductiveActorUntil(self, decade):
        max = 0
        mostProductiveActor = None
        for actor in self.prodGraph[decade]:
            if self.prodGraph.edges[decade, actor]['weight'] > max:
                max = self.prodGraph.edges[decade, actor]['weight']
                mostProductiveActor = actor
        return mostProductiveActor, max

    def dfs(self, year = None):
        if year == None:
            year = self.lastDecade

        for node in self.mainGraph:
            self.mainGraph.nodes[node]['color'] = 'white'
            self.mainGraph.nodes[node]['pred'] = -1


        for movie in self.mainGraph:
            if self.mainGraph.nodes[movie]['type'] == 'movie' and self.mainGraph.nodes[movie]['year'] <= year and self.mainGraph.nodes[movie]['color'] == 'white':
                self.dfsvisit(year, movie)

    def dfsvisit(self, year, node):
        self.mainGraph.nodes[node]['color'] = 'gray'
        self.dfstime += 1
        self.mainGraph.nodes[node]['discovery'] = self.dfstime
        for nextNode in self.mainGraph[node]:
            nn = self.mainGraph.nodes[nextNode]
            if nn['color'] == 'white' and (nn['type'] == 'actor' or (nn['type'] == 'movie' and nn['year'] <= year)):
                nn['pred'] = node
                self.dfsvisit(year, nextNode)
        self.mainGraph.nodes[node]['color'] = 'black'
        self.dfstime += 1
        self.mainGraph.nodes[node]['finish'] = self.dfstime
        print(node, self.mainGraph.nodes[node])

    def dfsiterative(self, year = None):
        stack = []
        if year == None:
            year = self.lastDecade

        for node in self.mainGraph:
            self.mainGraph.nodes[node]['color'] = 'white'
            self.mainGraph.nodes[node]['pred'] = -1

        maxDimension = 0
        for movie in self.mainGraph:
            dimension = 0
            m = self.mainGraph.nodes[movie]
            if m['type'] == 'movie' and m['year'] <= year and m['color'] == 'white':
                m['color'] = 'gray'
                self.dfstime += 1         
                m['discovery'] = self.dfstime
                dimension += 1
                stack.append(movie)
                while (len(stack)):
                    poppedNode = stack[-1]
                    stack.pop()
                    for nextNode in self.mainGraph[poppedNode]:
                        nn = self.mainGraph.nodes[nextNode]
                        if nn['color'] == 'white' and (nn['type'] == 'actor' or (nn['type'] == 'movie' and nn['year'] <= year)):
                            nn['pred'] = poppedNode
                            nn['color'] = 'gray'
                            self.dfstime += 1
                            nn['discovery'] = self.dfstime
                            dimension += 1
                            stack.append(nextNode)
                    pn = self.mainGraph.nodes[poppedNode]
                    pn['color'] = 'black'
                    self.dfstime += 1
                    pn['finish'] = self.dfstime
                    # print(poppedNode, pn)
            if dimension > maxDimension:
                maxDimension = dimension
                biggestCC = movie
        return biggestCC

    def getFilteredBiggestCC(self, year = None):
        if year == None:
            year = self.lastDecade

        for node in self.mainGraph:
            self.mainGraph.nodes[node]['color'] = 'white'
            self.mainGraph.nodes[node]['pred'] = None 


    def filteredBFS(self, start, year = None):
        m = self.mainGraph.nodes[start]
        queue = [start]
        i = 0
        while i < len(queue):
            current = queue[i]
            for nextNode in self.mainGraph[current]:
                nn = self.mainGraph.nodes[nextNode]
                if nn['color'] == 'white' and (nn['type'] == 'actor' or (nn['type'] == 'movie' and nn['year'] <= year)):
                    nn['color'] = 'gray'
                    nn['pred'] = current
                    queue.append(nextNode)
            i =+ 1
            self.mainGraph.nodes[current]['color'] = 'black'
        return queue


            



        

        
# START HERE
path = 'imdb-actors-actresses-movies.tsv'
# path = 'sample.tsv'
# path = 'test.tsv'
G = IMDBGraph()

print ('Fast start')
print(datetime.now().time())
G.createFromFile(path)
print(datetime.now().time())
print ('Fast finish')

print (G.mainGraph)
# print (G.prodGraph)

print ('DFS start')
print(datetime.now().time())

movie = G.dfsiterative()

print(datetime.now().time())
print ('DFS finish')

print (movie)

# print(datetime.now().time())
# actor, max = G.getMostProductiveActorUntil(1970)
# print (actor, max)

exit()