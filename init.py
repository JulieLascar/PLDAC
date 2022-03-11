import mysql.connector
import networkx as nx

connection_params = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : 'K@wa11',
    'database' : 'pldac'
}

r1 = 'SELECT * FROM users_0401_0415'
r2 = 'SELECT * FROM tweets_0401_0415'
r3 = 'SELECT tweet_id, source_user_id, target_user_id FROM user_mentions_0401_0415'
r4 = 'SELECT th.tweet_id as tweet_id, h.hash as hash FROM hashs_0401_0415 as h, tweet_hash_0401_0415 as th WHERE th.hash_id = h.hash_id'

def init():
    G = nx.MultiDiGraph()
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute(r1)
            result = c.fetchall()
            for t in result:
                G.add_node(int(t[0]), screen_name = t[1],
                                    name = t[2],
                                    location = t[3],
                                    url = t[4],
                                    description = t[5],
                                    created_at = t[6],
                                    followers_count = t[7],
                                    friends_count = t[8],
                                    statuses_count = t[9])
            c.execute(r2)
            result = c.fetchall()
            for t in result:
                if t[9] != None and t[5] in G.nodes and t[9] in G.nodes:
                    G.add_edge(int(t[5]), int(t[9]), type = 'reply',
                                                        tweet_id = t[0],
                                                        text = t[1],
                                                        geo_lat = t[3],
                                                        geo_long = t[4],
                                                        hash = [])
                if t[12] != None and t[5] in G.nodes and t[12] in G.nodes:
                    G.add_edge(int(t[5]), int(t[12]), type = 'quote',
                                                        tweet_id = t[0],
                                                        text = t[1],
                                                        geo_lat = t[3],
                                                        geo_long = t[4],
                                                        hash = [])
                if t[15] != None and t[5] in G.nodes and t[15] in G.nodes:
                    G.add_edge(int(t[5]), int(t[15]), type = 'retweet',
                                                        tweet_id = t[0],
                                                        text = t[1],
                                                        geo_lat = t[3],
                                                        geo_long = t[4],
                                                        hash = [])
            c.execute(r3)
            result = c.fetchall()
            for t in result:
                if t[1] in G.nodes and t[2] in G.nodes:
                    G.add_edge(t[1], t[2], type = 'mention',
                                            tweet_id = t[0],
                                            hash = [])
            '''c.execute(r4)
            result = c.fetchall()
            for t in result:
                for e in G.edges:
                    if G.edges[e]['tweet_id'] == t[0]:
                        G.edges[e]['hash'].append(t[1])'''
    return G



G = init()
nx.write_gpickle(G, 'graph.gpickle')
