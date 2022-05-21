import re

f = open("project/imdb-actors-actresses-movies.tsv", "r")
lines = f.readlines()
for line in lines:
    actor, movie = line.split("\t")
    print (actor, movie)
    year = re.search("(\()(\d\d\d\d)([\/[IXV]*]*\))", movie).group(2)
    print (year)

