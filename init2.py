import mysql.connector
import networkx as nx
import pickle as pkl

connection_params = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : 'K@wa11',
    'database' : 'pldac'
}

#r = "select user_id as source, in_reply_to_user_id as target, tweet_id from tweets_0401_0423 where user_id in (select user_id from users_0401_0423) and  in_reply_to_user_id in (select user_id from users_0401_0423) union select user_id as source, retweeted_user_id as target, tweet_id from tweets_0401_0423 where user_id in (select user_id from users_0401_0423) and retweeted_user_id in (select user_id from users_0401_0423) union select user_id as source, quoted_user_id as target, tweet_id from tweets_0401_0423 where user_id in (select user_id from users_0401_0423) and  quoted_user_id in (select user_id from users_0401_0423) union select source_user_id as source, target_user_id as target, tweet_id from user_mentions_0401_0423 where source_user_id in (select user_id from users_0401_0423) and target_user_id in (select user_id from users_0401_0423)"

r = "select user_id as source, in_reply_to_user_id as target, tweet_id from tweets_0401_0415 where user_id in (select user_id from users_0401_0415) and  in_reply_to_user_id in (select user_id from users_0401_0415) union select user_id as source, retweeted_user_id as target, tweet_id from tweets_0401_0415 where user_id in (select user_id from users_0401_0415) and retweeted_user_id in (select user_id from users_0401_0415) union select user_id as source, quoted_user_id as target, tweet_id from tweets_0401_0415 where user_id in (select user_id from users_0401_0415) and  quoted_user_id in (select user_id from users_0401_0415) union select source_user_id as source, target_user_id as target, tweet_id from user_mentions_0401_0415 where source_user_id in (select user_id from users_0401_0415) and target_user_id in (select user_id from users_0401_0415)"

r2 = 'select user_id from users_0401_0423'

def init():
    G = nx.MultiGraph()
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute(r)
            result = c.fetchall()
            print('Query OK')
            for t in result:
                G.add_edge(t[0], t[1], tweet_id = t[2])
    return G

def init2():
    G = nx.MultiDiGraph()
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute(r)
            result = c.fetchall()
            print('Query OK')
            for t in result:
                G.add_edge(t[0], t[1], tweet_id = t[2])
    return G

def tweets_rel():
    d = {}
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute('select tweet_id, in_reply_to_user_id, retweeted_user_id, quoted_user_id from tweets_0401_0415')
            result = c.fetchall()
            for v in result:
                if v[1] == None and v[2] == None and v[3] == None:
                    type = 's'
                elif v[1] != None and v[2] == None and v[3] == None:
                    type = 'a'
                elif v[1] == None and v[2] != None and v[3] == None:
                    type = 'r'
                elif v[1] == None and v[2] == None and v[3] != None:
                    type = 'q'
                elif v[1] != None and v[2] != None and v[3] == None:
                    type = 'ar'
                elif v[1] != None and v[2] == None and v[3] != None:
                    type = 'aq'
                elif v[1] == None and v[2] != None and v[3] != None:
                    type = 'rq'
                elif v[1] != None and v[2] != None and v[3] != None:
                    type = 'arq'
                d[v[0]] = type
    return d

def etiquetage():
    etiquettes = {}
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute('select * from etiquetage_0401_0415')
            result = c.fetchall()
            for t in result:
                etiquettes[t[0]] = {'cible': t[1], 'polarite': t[2]}
    return etiquettes

#G = init2()
#print(G)
#nx.write_gpickle(G, 'directed_graph.gpickle')

#d = tweets_rel()
#pkl.dump(d, open('tweets_rel.p', 'wb'))

e = etiquetage()
pkl.dump(e, open('etiquettes.p', 'wb'))
