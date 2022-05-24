import re
import numpy as np
import mysql.connector
import matplotlib.pyplot as plt
import pandas
from collections import Counter
import pickle

connection_params = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : 'masterDAC21$',
    'database' : 'twitter1'
}

L_promacron=['JeVoteMacron','voteMacron','MacronPresident']
L_profillon=['TousFillon','JeVoteFillon']
L_prolepen=['JeChoisisMarine','AvecMarine']
L_promelechon=['legoutdubonheur','MélenchonAu2emeTourCestPossible','JoursHeureux']
L_antimacron=['PoissonMacron','ToutSaufMacron','ImpostureMacron','StopMacron','BarbaraLefebvre','enmarchearriere','MacronPiègeÀCons','macrongate','EmmanuelHollande','LeVraiMacron']
L_antifillon=['FillonGate','PenelopeGate','PenelopeFillon','penelope','LeVraiFillon']
L_antilepen=['PasLePen']

def req1(r):
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute(r)
            result = c.fetchall()
            L = np.array(result)[:,0]
    return list(L)

a=[]
for hashtag in L_antimacron:
    r1=f"select t1.tweet_id from tweets_0401_0415 t1,tweet_hash_0401_0415 t2,hashs_0401_0415 t3 where (t1.tweet_id=t2.tweet_id and t2.hash_id=t3.hash_id and t3.hash='{hashtag}')"
    a+=req1(r1)

pickle.dump(a,open("antimacron.p","wb"))

f=[]
for hashtag in L_antifillon:
    r1=f"select t1.tweet_id from tweets_0401_0415 t1,tweet_hash_0401_0415 t2,hashs_0401_0415 t3 where (t1.tweet_id=t2.tweet_id and t2.hash_id=t3.hash_id and t3.hash='{hashtag}')"
    f+=req1(r1)

pickle.dump(f,open("antifillon.p","wb"))


l=[]
for hashtag in L_antilepen:
    r1=f"select t1.tweet_id from tweets_0401_0415 t1,tweet_hash_0401_0415 t2,hashs_0401_0415 t3 where (t1.tweet_id=t2.tweet_id and t2.hash_id=t3.hash_id and t3.hash='{hashtag}')"
    l+=req1(r1)

pm=[]
for hashtag in L_promacron:
    r1=f"select t1.tweet_id from tweets_0401_0415 t1,tweet_hash_0401_0415 t2,hashs_0401_0415 t3 where (t1.tweet_id=t2.tweet_id and t2.hash_id=t3.hash_id and t3.hash='{hashtag}')"
    pm+=req1(r1)

pf=[]
for hashtag in L_profillon:
    r1=f"select t1.tweet_id from tweets_0401_0415 t1,tweet_hash_0401_0415 t2,hashs_0401_0415 t3 where (t1.tweet_id=t2.tweet_id and t2.hash_id=t3.hash_id and t3.hash='{hashtag}')"
    pf+=req1(r1)

pl=[]
for hashtag in L_prolepen:
    r1=f"select t1.tweet_id from tweets_0401_0415 t1,tweet_hash_0401_0415 t2,hashs_0401_0415 t3 where (t1.tweet_id=t2.tweet_id and t2.hash_id=t3.hash_id and t3.hash='{hashtag}')"
    pl+=req1(r1)

pme=[]
for hashtag in L_promelechon:
    r1=f"select t1.tweet_id from tweets_0401_0415 t1,tweet_hash_0401_0415 t2,hashs_0401_0415 t3 where (t1.tweet_id=t2.tweet_id and t2.hash_id=t3.hash_id and t3.hash='{hashtag}')"
    pme+=req1(r1)

table = 'CREATE TABLE IF NOT EXISTS etiquetage_0401_0415(tweet_id bigint,cible varchar(255),polarité varchar(255))'
with mysql.connector.connect(**connection_params) as db:
    with db.cursor() as c:
        c.execute(table)

antimacron=pickle.load(open("antimacron.p","rb"))
antifillon=pickle.load(open("antifillon.p","rb"))


db= mysql.connector.connect(**connection_params)
c= db.cursor()
for id in antimacron:
    insert=f"insert into etiquetage_0401_0415 (tweet_id,cible,polarité) values ({id},'macron',-1) "
    c.execute(insert)

for id in antifillon:
    insert=f"insert into etiquetage_0401_0415 (tweet_id,cible,polarité) values ({id},'fillon',-1) "
    c.execute(insert)

for id in l:
    insert=f"insert into etiquetage_0401_0415 (tweet_id,cible,polarité) values ({id},'lepen',-1) "
    c.execute(insert)

for id in pm:
    if id not in antimacron :
        insert=f"insert into etiquetage_0401_0415 (tweet_id,cible,polarité) values ({id},'macron',1) "
        c.execute(insert)

for id in pf:
    if id not in antifillon :
        insert=f"insert into etiquetage_0401_0415 (tweet_id,cible,polarité) values ({id},'fillon',1) "
        c.execute(insert)

for id in pme:
    insert=f"insert into etiquetage_0401_0415 (tweet_id,cible,polarité) values ({id},'melenchon',1) "
    c.execute(insert)

for id in pl:
    if id not in l:
        insert=f"insert into etiquetage_0401_0415 (tweet_id,cible,polarité) values ({id},'lepen',1) "
        c.execute(insert)
      
db.commit()