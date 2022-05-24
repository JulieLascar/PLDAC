import pickle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.snowball import FrenchStemmer
from nltk.corpus import stopwords
import string
import re
import unicodedata
import time
from scipy.sparse import coo_matrix
from sklearn import svm
import sklearn.naive_bayes as nb
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
import mysql.connector
from sklearn.utils import shuffle

connection_params = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : 'masterDAC21$',
    'database' : 'twitter1'
}
r= 'select t2.text,t1.cible, t1.polarité from etiquetage_0401_0415 t1,tweets_0401_0415 t2 where t1.tweet_id=t2.tweet_id'
def req(r):
    with mysql.connector.connect(**connection_params) as db:
        with db.cursor() as c:
            c.execute(r)
            result = c.fetchall()
            L = np.array(result)[:,0:3]
    return L

L=req(r) 
textes_entiers=L[:,0]
data_cible=L[:,1]
data_label=L[:,2]

data_text=pickle.load(open("L_text_twitter1_etiquete_preprocess1.p","rb")) #chargement des données étiquetées prétraitées
data_text,data_cible,data_label=shuffle(data_text,data_cible,data_label)
assert(len(data_text)==len(data_label))

stemmer = FrenchStemmer()
sw = set(stopwords.words('french'))

class StemmedTfidfVectorizer(TfidfVectorizer):
    """
       class customisé pour vectoriser en tf-idf avec stemmer
    """
    def __init__(self, stemmer, preprocessor=None, stop_words=None, max_features=None, min_df=None, max_df=None, ngram_range=(1,1)):
        super(StemmedTfidfVectorizer, self).__init__(
            preprocessor=preprocessor,
            stop_words=stop_words,
            max_features=max_features,
            min_df=min_df, 
            max_df=max_df, 
            ngram_range=ngram_range
        )
        self.stemmer = stemmer

    def fit_transform(self, raw_documents, y=None): 
        """
            fit_transform avec time
        """
        start = time.time()
        res = super().fit_transform(raw_documents, y)
        end = time.time()
        print(f"Fit tranform on {self.__class__.__name__} with data of length {len(raw_documents)} exec in {end - start} secs")
        return res

    def transform(self, raw_documents): 
        """
            transform avec time
        """
        start = time.time()
        res = super().transform(raw_documents)
        end = time.time()
        print(f"tranform on {self.__class__.__name__} with data of length {len(raw_documents)} exec in {end - start} secs")
        return res    
        
    def build_analyzer(self):
        analyzer = super(StemmedTfidfVectorizer, self).build_analyzer()
        return lambda doc:(self.stemmer.stem(w) for w in analyzer(doc))


vectorizer = StemmedTfidfVectorizer(
preprocessor=None, 
stop_words=sw, 
stemmer=stemmer,
max_features=15000, 
min_df=2, 
max_df=0.7, 
ngram_range=(1,2)
)

X=vectorizer.fit_transform(data_text)
a=vectorizer.get_feature_names()
pickle.dump(a,open("features1_07complet.p","wb"))

clf_svm = svm.LinearSVC()
clf_svm.fit(X, data_label)
pickle.dump(clf_svm,open("clf_svm1_07complet.p","wb"))

L_text_cible_preprocess1 = pickle.load(open("L_tweet_cible_preprocess1.p","rb")) #chargement des tweets cibles prétraitees
X_t=vectorizer.transform(L_text_cible_preprocess1)
yhat=clf_svm.predict(X_t)
pickle.dump(yhat,open("pred_text_cible_preprocess1_07.p","wb"))

