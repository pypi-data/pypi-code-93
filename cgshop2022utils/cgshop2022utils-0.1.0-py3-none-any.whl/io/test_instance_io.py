import networkx as nx
import matplotlib.pyplot as plt
from random_instance import random_instance
from write import write_instance
from read import read_instance
from datetime import datetime

print("Generating " + datetime.now().strftime("%H:%M:%S"))
i = random_instance(n=50)
print("Drawing " + datetime.now().strftime("%H:%M:%S"))
nx.draw_networkx(i, pos={v: v for v in i.nodes}, with_labels=False, node_size=10)
plt.show()
print("Writing " + datetime.now().strftime("%H:%M:%S"))
write_instance(path="test",g=i,id='instance5',meta={"a":1,2:"b"})
print("Reading " + datetime.now().strftime("%H:%M:%S"))
d = read_instance(path="test")
print("Showing " + datetime.now().strftime("%H:%M:%S"))
nx.draw_networkx(d["graph"], pos={v: v for v in d["graph"].nodes}, with_labels=False, node_size=10)
plt.show()
print("Done " + datetime.now().strftime("%H:%M:%S"))
