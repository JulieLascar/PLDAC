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

r1='select hash_id,hash from hashs_0401_0415 '

def req1(r):
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute(r)
            result = c.fetchall()
            
    return result

L_hash = req1(r1) # Liste (id_hash,nom_hash)
dico_hash=dict()  # Dico : id_hash --> nom_hash
dico_hash_inv=dict() # Dico : nom_hash --> id_hash

for t in L_hash:
    dico_hash.update({t[0]:t[1]})
    dico_hash_inv.update({t[1]:t[0]})

#pickle.dump(dico_hash,open("dico_hash.p","wb")) #enregistrement du dico
#pickle.dump(dico_hash_inv,open("dico_hash_inv.p","wb")) #enregistrement du dico inversé

r2='select hash_id from tweet_hash_0401_0415 '
def req2(r):
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute(r)
            result = c.fetchall()
            L=np.array(result)[:,0]
    return L

L_hash =req2(r2)  # Liste de tous les hashtags 

hash_counts = Counter(L_hash) # Dictionnaire {id_hashtag : nombre} : hash_counts

# Les 200 hachtags prépondérants : d_hash_top
d=hash_counts.copy()
d_hash_top=dict()
for i in range(200):
    max_h=max(d,key=d.get)
    nb_hash=d[max_h]
    max_hash=dico_hash[max_h]
    d_hash_top[max_hash]=nb_hash
    d.pop(max_h)
    
dico_hash_candidats=dict() # dico : candidat--> liste des hastags associés
dico_hash_candidats['Macron']=['EmmanuelMacron','macron','EnMarche','Macron2017','MacronMarseille','JeVoteMacron','MacronPau','TeamMacron','voteMacron','MacronPresident']
dico_hash_candidats['Fillon']=['TousFillon','fillon','Fillon2017','JeVoteFillon','FillonPresident','FillonParis','ProjetFillon','FillonStrasbourg','FillonToulon','LR','FillonMarseille','FillonToulouse','FillonLyon','lesrepublicains','ProgrammeFillon','FrançoisFillon','FillonMontpellier','FillonClermont','FillonProvins']
dico_hash_candidats['Lepen']=['MLP2017','LePen2017','LePen','Marine2017','FN','AuNomDuPeuple','MLP','MarineLePen','AvecMarine','MarinePresidente','BordeauxMLP','Marine','JeChoisisMarine','LaFranceVoteMarine','MLPAjaccio','AjaccioMLP','world4marine']
dico_hash_candidats['Hamon']=['BHRennes','Hamon2017','Hamon','ps','hamonElysée','HamonTour','RevenuUniversel','FuturDésirable']
dico_hash_candidats['Melenchon']=['JLmelenchon','Mélenchon','JLM2017','JLMMarseille','JLMLille','FranceInsoumise','AvenirEnCommun','JLMChateauroux','LaForcedupeuple','JLM','insoumis','JoursHeureux','JLMFrance2','6eRépublique','LaFranceInsoumise','Melenchon2017','legoutdubonheur','MélenchonAu2emeTourCestPossible']
dico_hash_candidats['DupontAignan']=['DupontAignan','NDA','NDA2017']
dico_hash_candidats['antiMacron']=['PoissonMacron','ToutSaufMacron','ImpostureMacron','StopMacron','BarbaraLefebvre','enmarchearriere','MacronPiègeÀCons','macrongate','EmmanuelHollande','LeVraiMacron']
dico_hash_candidats['antiFillon']=['FillonGate','PenelopeGate','PenelopeFillon','penelope','LeVraiFillon']
dico_hash_candidats['Poutou']=['Poutou']
dico_hash_candidats['Arthaud']=['Arthaud']

pickle.dump(dico_hash_candidats,open("dico_hash_candidats.p","wb")) #enregistrement du dico candidats

dico_hash_candidats=pickle.load(open("dico_hash_candidats.p","rb"))
H_candidats=dict() # Histogramme des candidats
for c in dico_hash_candidats.keys():
    H_candidats[c]=0
    for h in dico_hash_candidats[c]:
        H_candidats[c] += d_hash_top[h]
        d_hash_top.pop(h)

H_candidats={k: v for k, v in sorted(H_candidats.items(), key=lambda item: item[1],reverse=True)}

#print(H_candidats)

df = pandas.DataFrame.from_dict(H_candidats, orient='index')
df.plot(kind='bar',figsize = (15,15),title='Les hashtags des candidats du 1er au 15 avril 2017')
plt.savefig("Histogramme_candidats.png")

# Mise à jour de d_hash_top
L_médias=['TF1','RTLMatin','LeGrandDebat','LEmissionPolitique','onpc','bfmtv','BourdinDirect','LCI','cdanslair','cnews','beurfm','france2','DemainPrésident','granddebat','19hruthelkrief','rediff','cavous','DebatBfm','BFM','LeGrandJury','BFMPolitique','TDinfos','Bourdin','Emissionpolitique','Les4Vérités','le79inter','Replay']
d=H_candidats.copy()
d['médias']=0
for h in L_médias:
    d['médias'] += d_hash_top[h]
    d_hash_top.pop(h)

d_hash_top.update(d)
#print(d_hash_top)

# Histogramme des 20 hachtags prépondérants 
d=d_hash_top.copy()

Histo_hash=dict()
for i in range(20):
    max_h=max(d,key=d.get)
    nb_hash=d[max_h]
    Histo_hash[max_h]=nb_hash
    d.pop(max_h)

#print(Histo_hash)
df = pandas.DataFrame.from_dict(Histo_hash, orient='index')
df.plot(kind='bar',figsize = (15,20),title='Les hashtags prépondérants du 1er au 15 avril 2017')
plt.savefig("Histogramme_hashtag20.png")
