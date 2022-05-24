import re
import numpy as np
import mysql.connector
import unicodedata
import string
import pickle


# Chargement des données
connection_params = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : 'masterDAC21$',
    'database' : 'twitter1'
}

r1='select text from tweets_0401_0415'

r2='select t1.text from tweets_0401_0415 t1,tweet_hash_0401_0415 t2 where t1.tweet_id=t2.tweet_id '

r3= 'select t2.text,t1.cible, t1.polarité from etiquetage_0401_0415 t1,tweets_0401_0415 t2 where t1.tweet_id=t2.tweet_id '

def req(r):
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute(r)
            result = c.fetchall()
            L = np.array(result)[:,0]
    return L
    

L_text_twitter1= req(r1) # liste des textes de twitter1

L_text_twitter1_hash= req(r2) # liste des textes de twitter1 qui ont des hashtags        
#pickle.dump(L_text_twitter1_hash,open("L_text_twitter1_hash.p","wb"))

L_text_twitter1_etiquete=req(r3)
#print(L_text_twitter1_etiquete)

L_tweet_cible=pickle.load(open('L_IdTextCible.p','rb'))
L_text_cible=np.array(list(L_tweet_cible.values()))[:,0]

punc = string.punctuation  # recupération de la ponctuation
punc += '\n\r\t'
punc1=punc.replace('#','')
punc2=punc1.replace('_','')
punc3=punc2.replace('@','')
punc4=punc3.replace('!','')

dico_candidat=dict() # dictionnaire des pseudos des candidats (plus large que celui des hashtags)
dico_candidat['Macron']=['EmmanuelMacron', 'Emmanuel Macron','EnMarche', 'Macron2017' ,'MacronMarseille', 'MacronPau' ,'TeamMacron', 'emmanuel macron' ,'macron']
dico_candidat['Fillon']=['françois fillon','françoisfillon','fillon','Fillon2017','FillonPresident','FillonParis','ProjetFillon','FillonStrasbourg','FillonToulon','LR','FillonMarseille','FillonToulouse','FillonLyon','lesrepublicains','ProgrammeFillon','FrançoisFillon','FillonMontpellier','FillonClermont','FillonProvins']
dico_candidat['Lepen']=['LePen2017', 'MLP2017','Marine Le Pen','LePen','Le Pen','Marine2017','FN','AuNomDuPeuple','MLP','MarineLePen','AvecMarine','MarinePresidente','BordeauxMLP','Marine','JeChoisisMarine','LaFranceVoteMarine','MLPAjaccio','AjaccioMLP','world4marine']
dico_candidat['Hamon']=['BHRennes','Hamon2017','Hamon','ps','hamonElysée','HamonTour','RevenuUniversel','FuturDésirable']
dico_candidat['Melenchon']=['JLmelenchon','jean luc melenchon','JLMelenchon','Mélenchon','JLM2017','JLMMarseille','JLMLille','JLMLeHavre','FranceInsoumise','AvenirEnCommun','JLMChateauroux','LaForcedupeuple','JLM','insoumis','JoursHeureux','JLMFrance2','6eRépublique','LaFranceInsoumise','Melenchon2017','legoutdubonheur','MélenchonAu2emeTourCestPossible']
dico_candidat['DupontAignan']=['NDA2017','DupontAignan','NDA']
dico_candidat['médias']=['RTLMatin', 'TF1','LeGrandDebat','LEmissionPolitique','onpc','bfmtv','BourdinDirect','LCI','cdanslair','cnews','beurfm','france2','DemainPrésident','granddebat','19hruthelkrief','rediff','cavous','DebatBfm','BFM','LeGrandJury','BFMPolitique','TDinfos','Bourdin','Emissionpolitique','Les4Vérités','le79inter','Replay']
#dico_candidat['antiMacron']=['PoissonMacron', 'ToutSaufMacron','ImpostureMacron','StopMacron','BarbaraLefebvre','enmarchearriere','MacronPiègeÀCons','macrongate','EmmanuelHollande','LeVraiMacron']
#dico_candidat['antiFillon']=['FillonGate','PenelopeGate','PenelopeFillon','penelope','LeVraiFillon']


def transfo_pseudo(txt):
    """transforme le pseudo du candidat en mot-clé candidat """
    for i in dico_candidat.keys():
        for j in dico_candidat[i]:
            txt=re.sub(j,i,txt)
    return (txt)


def transfo_url(txt):
    """remplace les liens URL par lien_url"""
    txt=re.sub(r'\bhttp[^ ]+',"lien_url",txt)
    txt=re.sub(r'\bwww[^ ]+',"lien_url",txt)
    return txt
   

def marqueur_maj(txt):
    """ On met un marqueur aux mots en majuscules : maj mot """
    L=txt.split()
    for w in L :
        if w == w.upper() and len(w)>3 and not('#'in w) and not('@' in w):
            try:
                w1='maj '+w
                txt=re.sub(w,w1,txt)
            except:
                print('erreur majuscule')
    return txt


def pre_process(txt):
    #pré-traitement des données : la base
    txt= transfo_url(txt)
    txt=transfo_pseudo(txt)
    txt = re.sub(r'\d+', '', txt)
    txt = unicodedata.normalize('NFD', txt).encode('ascii', 'ignore').decode("utf-8")
    txt = txt.translate(str.maketrans(punc4, ' ' * len(punc4))) 
    txt = txt.lower()
    return txt

def pre_process2(txt):
    #pré-traitement des données : base + suppression des hashtags
    txt=re.sub(r'\#[^ ]+',"",txt)
    txt= transfo_url(txt)
    txt=transfo_pseudo(txt)
    txt = re.sub(r'\d+', '', txt)
    txt = unicodedata.normalize('NFD', txt).encode('ascii', 'ignore').decode("utf-8")
    txt = txt.translate(str.maketrans(punc4, ' ' * len(punc4)))
    txt = txt.lower()
    while '  ' in txt : 
        txt=re.sub('  '," ",txt)
    return txt

def pre_process3(txt):
    #pré-traitement des données : base + suppression des hashtags + suppression des "rt @username"
    txt=re.sub(r'\#[^ ]+',"",txt)
    txt= transfo_url(txt)
    txt=transfo_pseudo(txt)
    txt = re.sub(r'\d+', '', txt)
    txt = unicodedata.normalize('NFD', txt).encode('ascii', 'ignore').decode("utf-8")
    txt = txt.translate(str.maketrans(punc4, ' ' * len(punc4)))
    txt = txt.lower()
    txt = re.sub(r'\brt [^ ]+','', txt)
    while '  ' in txt : 
        txt=re.sub('  '," ",txt)
    return txt


L_text_etiquete_preprocess=[]
for t in L_text_twitter1_etiquete:
       L_text_etiquete_preprocess.append(pre_process(t))

pickle.dump(L_text_etiquete_preprocess,open("L_text_etiquete_preprocess.p","wb"))

print(L_text_etiquete_preprocess[0:10])