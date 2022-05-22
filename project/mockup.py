import re
import networkx as nx
G = nx.Graph()

# RE
# will work on movie part of string 
# first group an opening parenthesis
# second group the year (4 digits)
# third optional group slash with roman numbers
# four group a closing parenthesis
p = re.compile("(\()(\d\d\d\d)([/IXV])*(\))")

f = open("project/imdb-actors-actresses-movies.tsv", "r")
lines = f.readlines()
for line in lines:
    actor, movie = line.split("\t")


    y = p.search(movie)
    #discard not matching string, e.g. lines without year see Aamundson
    if y:
        # get second group, 4 digits i.e. the year
        year = y.group(2)
        G.add_node(actor, type="actor")
        G.add_node(movie, type="movie", year=year)
        G.add_edge(actor, movie)

print (G)