import random
f = open("imdb-actors-actresses-movies.tsv", "r")
g = open("sample.tsv", "w")
lines = f.readlines()
for line in lines:
    lucky = random.randint(0,50)
    if (lucky == 13):
        g.write(line)

f.close
g.close


