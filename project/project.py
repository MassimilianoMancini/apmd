import os
import json
import re

authors = {}
p = re.compile("- _+_")
"""
for filename in os.listdir("sequences"):
    with open(os.path.join("sequences", filename), 'r') as f:
        comments = json.load(f)['comments']

        G.add_node(nodeName)
        print(f"Adding node [{nodeName}]\r", end = "")
"""

with open(os.path.join("sequences"), "A000045.json", 'r') as f:
    comments = json.load(f)['comments']
    



print(G)