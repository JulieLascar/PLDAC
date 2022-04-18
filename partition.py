import networkx as nx
import community as community_louvain
import pickle # ou pickle5 selon la version de python
import time
import numpy as np

G = pickle.load(open('graph_.gpickle', 'rb'))

def subGraph(G, max):
    Gp = nx.MultiDiGraph()
    current = np.random.choice(list(G.nodes))
    do = []
    while Gp.number_of_nodes() < max:
        Gp.add_node(current)
        Gp.add_edges_from(G.edges(current))
        do.append(current)
        new = np.random.choice(list(Gp.nodes()))
        while new in do:
            new = np.random.choice(list(Gp.nodes()))
        current = new
    print(do)
    return Gp

#Gp = subGraph(G, 1000)

G = G.to_undirected()

started = time.time()

partition = community_louvain.best_partition(G)

ended = time.time()
print(ended - started) 
pickle.dump(partition, open('partition_.p', 'wb'))
