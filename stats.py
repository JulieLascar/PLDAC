from cmath import inf
from hashlib import new
from multiprocessing import connection
from operator import inv
from random import random
from sqlite3 import connect
from itsdangerous import exc
import networkx as nx
import community as community_louvain
import pickle as pkl
import matplotlib.pyplot as plt
import numpy as np
from scipy import rand
import seaborn as sn

def communities_graph(G, partition):
    CG = nx.Graph()
    CG.add_nodes_from(list(partition.values()))
    for e in G.edges:
        if partition[e[0]] != partition[e[1]]:
            CG.add_edge(partition[e[0]], partition[e[1]])
    return CG

def partition(communities):
    partition = {}
    for i in range(len(communities)):
        for n in communities[i]:
            partition[n] = i
    return partition

def inv_partition(partition):
    ip = {v: [] for v in partition.values()}
    for k in partition.keys():
        ip[partition[k]].append(k)
    return ip

def densities(G, inv_partition):
    densities = []
    for v in inv_partition.values():
        sg = G.subgraph(v)
        densities.append(nx.density(sg))
    return densities

def diameters(G, inv_partition):
    diameters = []
    for v in inv_partition.values():
        sg = G.subgraph(v)
        diameters.append(nx.diameter(sg))
    return diameters

def process_tweets(tweets):
    tweets_p = {}
    for k, v in tweets.items():
        type = ''
        if v['in_reply_to_user_id'] == None and v['retweeted_user_id'] == None and v['quoted_user_id'] == None:
            type = 's'
        elif v['in_reply_to_user_id'] != None and v['retweeted_user_id'] == None and v['quoted_user_id'] == None:
            type = 'a'
        elif v['in_reply_to_user_id'] == None and v['retweeted_user_id'] != None and v['quoted_user_id'] == None:
            type = 'r'
        elif v['in_reply_to_user_id'] == None and v['retweeted_user_id'] == None and v['quoted_user_id'] != None:
            type = 'q'
        elif v['in_reply_to_user_id'] != None and v['retweeted_user_id'] != None and v['quoted_user_id'] == None:
            type = 'ar'
        elif v['in_reply_to_user_id'] != None and v['retweeted_user_id'] == None and v['quoted_user_id'] != None:
            type = 'aq'
        elif v['in_reply_to_user_id'] == None and v['retweeted_user_id'] != None and v['quoted_user_id'] != None:
            type = 'rq'
        elif v['in_reply_to_user_id'] != None and v['retweeted_user_id'] != None and v['quoted_user_id'] != None:
            type = 'arq'
        tweets_p[v['tweet_id']] = v
        tweets_p[v['tweet_id']].update({'type': type})
    return tweets_p

def edges_colors(c, tweets, rel_colors):
    colors = []
    for e in c.edges(data=True):
        try:
            colors.append(rel_colors[tweets[e[2]['tweet_id']]])
        except:
            pass
    return colors

def rel(tweets_c, tweets):
    rel = []
    for t in tweets_c:
        try:
            rel.append(tweets[t]['type'])
        except:
            rel.append('m')
    return rel

def etiquetage(G, etiquettes):
    for e in G.edges(data=True):
        try:
            etiquettes[e[2]['tweet_id']]['source'] = e[0]
            etiquettes[e[2]['tweet_id']]['target'] = e[1]
        except:
            pass
    return etiquettes

def label_communities(etiquettes, communities):
    label_comm = []
    for k, v in etiquettes.items():
        for c in communities:
            try:
                if v['source'] in c and v['target'] in c:
                    label_comm.append(communities.index(c))
            except:
                pass
    return label_comm

def rt2id(tweets):
    r2t = {t['retweeted_status_id']: [] for t in tweets.values() if t['type'] == 'r'}
    for t in tweets.values():
        if t['type'] == 'r':
            r2t[t['retweeted_status_id']].append(t['tweet_id'])
    return r2t

def propage(tweets_g, r2t, etiquettes):
    new_label = {}
    while True:
        for id in tweets_g:
            if id in etiquettes.keys() and id in r2t.keys():
                for r in r2t[id]:
                    new_label[r] = etiquettes[id]
        if new_label = {}:
            return etiquettes
        etiquettes.update(new_label)
    return etiquettes
            

# chargement du graphe d'interactions

G = nx.read_gpickle('directed_graph.gpickle')
print(G)

UG = nx.read_gpickle('undirected_graph.gpickle')
print(UG)

'''
c = np.random.randint(0, 10000, G.number_of_nodes())
p = nx.spiral_layout(G)

nx.draw(G, node_size=1, width=0.2, node_color=c, pos=p)
plt.show()
'''

# Analyse du graphe d'interactions

## densité
print("densité :", nx.density(G))

## composantes connexes
connected_components = list(nx.connected_components(UG))
len(connected_components)
connected_components_lens = [len(c) for c in connected_components]
print('plus petite composante connexe :', np.min(connected_components_lens))
print('plus grande composante connexe :', np.max(connected_components_lens))
print('taille moyenne des composantes connexes :', np.mean(connected_components_lens))
print('taille médianne des composantes connexes :', np.median(connected_components_lens))

## degrés
degree = np.array(list(dict(nx.degree(G)).values()))
print('degre min :', np.min(degree))
print('degre max :', np.max(degree))
print('degre median :', np.median(degree))
print('degre moyen :', np.mean(degree))
print('dispersion des degres :', np.std(degree))

plt.hist(degree[degree <= np.mean(degree)])
plt.xlabel('degrés des sommets')
plt.ylabel('nombre de sommets')
plt.show()

## centralité

### centralité de degré

deg_cent = np.array(list(dict(nx.degree_centrality(G)).values()))
print('centralité de degré min :', np.min(deg_cent))
print('centralité de degré max :', np.max(deg_cent))
print('centralité de degré medianne :', np.median(deg_cent))
print('centralité de degré moyenne :', np.mean(deg_cent))
print('dispersion des centralités de degré :', np.std(deg_cent))

plt.hist(deg_cent[deg_cent <= np.mean(deg_cent)])
plt.xlabel('centralités de degré')
plt.ylabel('nombre de sommets')
plt.show()

### pagerank
pagerank = nx.pagerank(G)

# Détection des communautés

best_communities = pkl.load(open('best_communities.p', 'rb'))

low_resolution_communities = pkl.load(open('low_resolution_communities.p', 'rb'))

# Analyse des partitions créées

best_partition = partition(best_communities)
best_inv_partition = inv_partition(best_partition)
low_resolution_partition = partition(low_resolution_communities)
low_resolution_inv_partition = inv_partition(low_resolution_partition)

print(len(best_communities))
print(len(low_resolution_communities))

print('best modularity :', nx.algorithms.community.modularity(G, best_communities))
print('low resolution modularity :', nx.algorithms.community.modularity(G, low_resolution_communities))


## taille des communautés

best_communities_size = [len(c) for c in best_communities]
low_resolution_size = [len(c) for c in low_resolution_inv_partition.values()]

print("taille minimale d'une communauté :", np.min(best_communities_size))
print("taille moyenne d'une communauté :", np.mean(best_communities_size))
print("taille médianne d'une communauté :", np.median(best_communities_size))
print("taille maximale d'une communauté :", np.max(best_communities_size))

# densités des communautés

best_communities_densities = densities(G, best_inv_partition)

# Analyse du graphe des communautés

best_communities_graph = communities_graph(G, best_partition)
print("densité minimale d'une communauté :", np.min(best_communities_densities))
print("densité maximale d'une communauté :", np.max(best_communities_densities))
print("densité moyenne d'une communauté :", np.mean(best_communities_densities))
print("densité médianne d'une communauté :", np.median(best_communities_densities))

'''
IG = community_louvain.induced_graph(partition, G)
nx.write_gpickle(IG, 'induced_graph.gpickle')
IG = nx.read_gpickle('induced_graph.gpickle')
'''

#IG = communities_graph(G, best_partition)
IG = nx.read_gpickle('induced_graph.gpickle')
print(IG)

#nx.write_gpickle(IG, 'induced_graph.gpickle')

print('densité :', nx.density(IG))

c = np.random.randint(0, 10000, IG.number_of_nodes())
l = [len(c) for c in best_communities]
size = l/np.max(l)*5000
p = nx.spiral_layout(IG)

nx.draw_networkx_nodes(IG, node_size=size, node_color=c, pos=p)
nx.draw_networkx_edges(IG, pos=p, width=0.1)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['bottom'].set_visible(False)
plt.show()

# description interne des communautés

users = pkl.load(open('users.p', 'rb'))
tweets = pkl.load(open('tweets.p', 'rb'))
#tweets = process_tweets(tweets)

#pkl.dump(tweets, open('tweets.p', 'wb'))

# dictionnaire de couleurs

rel_colors = {'a': 'b', 'r': 'g', 'q': 'r', 'ar': 'c', 'aq': 'm', 'rq': 'y'}

bigger_communities = np.argsort(best_communities_size)[-100:-10]

random_communities = np.random.choice(bigger_communities, 3)
print(random_communities)
# 23, 115, 732 

c1 = G.subgraph(best_communities[random_communities[0]])
c2 = G.subgraph(best_communities[random_communities[1]])
c3 = G.subgraph(best_communities[random_communities[2]])

# c1

print('taille :', c1.number_of_nodes())
print('arcs :', c1.number_of_edges())
print('densité :', nx.density(c1))

nx.draw_shell(c1)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['bottom'].set_visible(False)
plt.show()

degree_c1 = list(dict(nx.degree(c1)).values())

plt.hist(degree_c1)
plt.xlabel('degrés des sommets')
plt.ylabel('nombre de sommets')
plt.show()

tweets1 = [e[2]['tweet_id'] for e in c1.edges(data=True)]
rel_type = rel(tweets1, tweets)

labels = ['a', 'r', 'q', 'a+r', 'a+q', 'r+q', 'a+r+q', 'm']

rel_vec = [rel_type.count(t) for t in labels]

plt.bar(labels, rel_vec)
plt.xlabel('types de relation')
plt.ylabel("nombre d'arcs")
plt.show()

# c2

print('taille :', c2.number_of_nodes())
print('arcs :', c2.number_of_edges())
print('densité :', nx.density(c2))

nx.draw_shell(c2, node_color='y', node_size=10)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['bottom'].set_visible(False)
plt.show()

degree_c2 = list(dict(nx.degree(c2)).values())

plt.hist(degree_c2)
plt.xlabel('degrés des sommets')
plt.ylabel('nombre de sommets')
plt.show()

tweets2 = [e[2]['tweet_id'] for e in c2.edges(data=True)]
rel_type = rel(tweets2, tweets)

rel_vec = [rel_type.count(t) for t in labels]

plt.bar(labels, rel_vec)
plt.xlabel('types de relation')
plt.ylabel("nombre d'arcs")
plt.show()

# c3

print('taille :', c3.number_of_nodes())
print('arcs :', c3.number_of_edges())
print('densité :', nx.density(c3))

nx.draw_shell(c3, node_color='r')
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['bottom'].set_visible(False)
plt.show()

degree_c3 = list(dict(nx.degree(c3)).values())

plt.hist(degree_c3)
plt.xlabel('degrés des sommets')
plt.ylabel('nombre de sommets')
plt.show()

tweets3 = [e[2]['tweet_id'] for e in c3.edges(data=True)]
rel_type = rel(tweets3, tweets)

rel_vec = [rel_type.count(t) for t in labels]

plt.bar(labels, rel_vec)
plt.xlabel('types de relation')
plt.ylabel("nombre d'arcs")
plt.show()

# combinaison des approches

etiquettes = pkl.load(open('etiquettes.p', 'rb'))

#etiquettes = etiquetage(G, etiquettes)

#pkl.dump(etiquettes, open('etiquettes.p', 'wb'))

label_comm = label_communities(etiquettes, best_communities)
#pkl.dump(label_comm, open('label_communities.p', 'wb'))

len(set(label_comm))

plt.bar([str(c) for c in set(label_comm)], [label_comm.count(c) for c in set(label_comm)])
plt.xlabel('communautés')
plt.ylabel("nombre d'étiquettes")
plt.xticks(rotation=90)
plt.show()

# étude des communautés étiquetées

c9 = G.subgraph(best_inv_partition[9]).copy()
nx.write_gpickle(c9, 'c9.gpickle')

print('taille :', c9.number_of_nodes())
print('arcs :', c9.number_of_edges())
print('densité :', nx.density(c9))

labels9 = [(v['cible'], v['polarite']) for v in etiquettes.values()]

barres_n = [labels9.count(('melenchon', '-1')), labels9.count(('macron', '-1')), labels9.count(('lepen', '-1')), labels9.count(('fillon', '-1'))]
barres_p = [labels9.count(('melenchon', '1')), labels9.count(('macron', '1')), labels9.count(('lepen', '1')), labels9.count(('fillon', '1'))]

target = list(set(np.array(labels9)[:,0]))

plt.bar(target, [barres_n[i] + barres_p[i] for i in range(len(barres_n))], color='g', label='positif')
plt.bar(target, barres_n, color='r', label='négatif')
plt.legend()
plt.xlabel('cible des tweets')
plt.ylabel('nombre de tweets')
plt.show()

# propagation des étiquettes

labels = ['a', 'r', 'q', 'a+r', 'a+q', 'r+q', 'a+r+q', 'm']

tweets9 = [e[2]['tweet_id'] for e in c9.edges(data=True)]
rel_type = rel(tweets9, tweets)

rel_vec = [rel_type.count(t) for t in labels]

plt.bar(labels, rel_vec)
plt.xlabel('types de relation')
plt.ylabel("nombre d'arcs")
plt.show()

r2t = rt2id(tweets)
pkl.dump(r2t, open('rt2id.p', 'wb'))

etiquettes_new = propage(tweets9, r2t, etiquettes)

random_tweets = np.random.choice(list(etiquettes_new.keys()), 5)

for id in random_tweets:
    print('----------------------------')
    print(tweets[id]['text'])
    print('cible :', etiquettes_new[id]['cible'])
    print('polarité :', etiquettes_new[id]['polarite'])
    print('----------------------------')