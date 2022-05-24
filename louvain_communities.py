import pickle as pkl
import networkx as nx

UG = nx.read_gpickle('undirected_graph.py')

communities = nx.algorithms.community.louvain_communities(UG)

pkl.dump(communities, 'best_communities.p', 'wb'))
