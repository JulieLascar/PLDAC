import mysql.connector
import networkx as nx

connection_params = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : 'K@wa11',
    'database' : 'pldac'
}

r = "select user_id as source, in_reply_to_user_id as target, tweet_id from tweets_0401_0415 where user_id in (select user_id from users_0401_0415) and  in_reply_to_user_id in (select user_id from users_0401_0415) union select user_id as source, retweeted_user_id as target, tweet_id from tweets_0401_0415 where user_id in (select user_id from users_0401_0415) and retweeted_user_id in (select user_id from users_0401_0415) union select user_id as source, quoted_user_id as target, tweet_id from tweets_0401_0415 where user_id in (select user_id from users_0401_0415) and  quoted_user_id in (select user_id from users_0401_0415) union select source_user_id as source, target_user_id as target, tweet_id from user_mentions_0401_0415 where source_user_id in (select user_id from users_0401_0415) and target_user_id in (select user_id from users_0401_0415)"

r2 = 'select user_id from users_0401_0415'

def init():
    G = nx.MultiDiGraph()
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute(r)
            result = c.fetchall()
            for t in result:
                G.add_edge(int(t[0]), int(t[1]), tweet_id = int(t[2]))
    return G

G = init()
nx.write_gpickle(G, 'graph_.gpickle')
