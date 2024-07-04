import networkx as nx

from database.DAO import DAO
from model.model import Model


myLinee = DAO.getAllLinee()

mymodel = Model()
mymodel.buildGraph()

print(f"The graph has {mymodel.getNumNodes()} nodes.")
print(f"The graph has {mymodel.getNumEdges()} edges.")

edges = nx.bfs_edges(mymodel._grafo, mymodel.fermate[0])
#print(list(edges))
for u, v in edges:
    print(v)
