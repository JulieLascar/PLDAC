import numpy as np
import re
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

r1='select tweet_id,hash_id from tweet_hash_0401_0415'

def req1(r):
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute(r)
            result = c.fetchall()
            L = np.array(result)
    return L
    
L=req1(r1)

#données sauvegardées
'''
r2='select tweet_id,text from tweets_0401_0415'

def req2(r):
    d=dict()
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute(r)
            result = c.fetchall()
            for t in result :
                d.update({t[0]:t[1]})
    return d

dico_tweet=req2(r2)
pickle.dump(dico_tweet,open("dico_tweet.p","wb"))'''

dico_hash= pickle.load(open("dico_hash.p","rb")) # chargement du dico : id_hash --> nom_hash
dico_hash_inv= pickle.load(open("dico_hash_inv.p","rb")) # chargement du dico : nom_hash --> id_hash

# Création d'un dictionnaire --> clé : id du tweet   valeur : liste des id hastags 
dico_tweet_hash=dict()
for i in range(len(L)):
    t = L[i,0]
    h = L[i,1]
    if t in dico_tweet_hash.keys() :
        dico_tweet_hash[t].append(dico_hash[h])
    else :
       dico_tweet_hash[t] = [dico_hash[h]] 

dico_hash_candidats=pickle.load(open("dico_hash_candidats.p","rb")) # chargement du dico : candidat -->liste hash

d_init=dict()
for c in dico_hash_candidats.keys():
    d_init[c]=0

def tri_hash(tweet_id):
    """id tweet ---> dico: nb de hashtag pour chaque candidat"""
    d=dict()  # Initialisation d'un dictionnaire pour compter le nombre de hastags de chaque candidat
    for c in dico_hash_candidats.keys():
        d[c]=0 
    try :
        L_h=dico_tweet_hash[tweet_id] # On récupère la liste des hashtags contenus dans le tweet
        for h in L_h: # On compte le nombre de hastags du tweet qui sont présents dans la liste de ceux des candidats
            for candidat,L in dico_hash_candidats.items():
                if h in L:
                    d[candidat]+=1
        return d
    except :
        return d

# test
#print(tri_hash(847599362809004036))

def cible1 (tweet_id):
    """retourne la cible du tweet : cible s'il n y a qu'un seul candidat hashtagué"""
    t =  tri_hash(tweet_id)
    if len(list(filter(None,t.values()))) != 1 :
        return None
    else :
        for c in dico_hash_candidats.keys():
            if t[c] != 0:
                return c

# test1 # cas positif
#print(tri_hash(847599362809004036))
#print(cible1(847599362809004036))
# test2 # plusieurs candidats
#print(tri_hash(847599615851470848))
#print(cible1(847599615851470848))
# test3 # 0 candidats
#print(tri_hash(847599611774513157))
#print(cible1(847599611774513157))

# Dans un premier temps, on considère uniquement les tweets avec hashtags.
tweets_cible=dict()
tweets_noncible=[]

for t in dico_tweet_hash.keys():
    c =cible1(t)
    if c != None :
        tweets_cible[t] = c
    else :
        tweets_noncible.append(t)

print('Parmi les tweets qui ont des hashtags:')
print('nombre de tweets avec cible',len(tweets_cible))
print('nombre de tweets sans cible',len(tweets_noncible))
print('nombre total de tweet',len(dico_tweet_hash))

v=tweets_cible.values()
c=Counter(v)
print('Répartition des cibles',c)


dico_tweet = pickle.load(open("dico_tweet.p","rb"))

L_t= list(tweets_cible.keys())

def appli_cible (nb) :
    '''nb: nb de tweets que l'on veut tester. Pour chaque tweet, on donne la cible réelle, et le sentiment. On enregistre les résulats dans un fichier.'''
    R_cible = pickle.load(open("R_cible.p","rb"))
    R_polarite = pickle.load(open("R_polarite.p","rb"))
    np.random.shuffle(L_t)
    cpt=0
    nsp=0
    for t in L_t[:nb]:
        print ("\n",dico_tweet[t])
        r=input("Quel candidat vise ce tweet ?\n Réponses attendues: Macron,Fillon,Melenchon,Lepen,Hamon,DupontAignan,Poutou,Arthaud,antiMacron,antiFillon,nesaispas ") 
        if str(r) == 'nesaispas':
            nsp+=1
        if str(r) == cible1(t):
            cpt +=1
        s=input("\nLe tweet est il positif ou négatif par rapport au candidat choisi? Répondre 1 ou -1 ou 0 si indécis\n")
        R_polarite[t]=s    
    R_cible.append((cpt,nb))
    pickle.dump(R_cible,open("R_cible.p","wb"))
    pickle.dump(R_polarite,open("R_polarite.p","wb"))
    return cpt*100/nb


#Attention! Risque d'effacer les données! Seulemet pour initialiser.
#R_cible=[]
#R_polarite=dict()
#pickle.dump(R_cible,open("R_cible.p","wb"))
#pickle.dump(R_polarite,open("R_polarite.p","wb"))

appli_cible(2)

R_cible = pickle.load(open("R_cible.p","rb"))
R_polarite = pickle.load(open("R_polarite.p","rb"))
print(R_cible)
print(R_polarite)

    
  