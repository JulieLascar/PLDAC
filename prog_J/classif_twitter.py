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


text=pickle.load(open("L_text_twitter1_pre_process2.p","rb")) # données pré-traitées

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
        
    def build_analyzer(self):
        analyzer = super(StemmedTfidfVectorizer, self).build_analyzer()
        return lambda doc:(self.stemmer.stem(w) for w in analyzer(doc))


vectorizer = StemmedTfidfVectorizer(
    stop_words=sw, 
    stemmer=stemmer,
    max_features=15000, 
    min_df=2, 
    max_df=0.7, 
    ngram_range=(1,2)
)

X_twitter = vectorizer.fit_transform(text) # vectorisation des données twitter
X_twitter.toarray()
X_twitter = coo_matrix(X_twitter)
pickle.dump(X_twitter,open("X_twitter_vect.p","wb")) # enregistrement des données vectorisées

clf=pickle.load(open("svm.p","rb")) #chargement du modèle svm
pred_svm=clf.predict(X_twitter) #calcul des prédictions svm des données twitter
pickle.dump(pred_svm,open("pred_svm.p","wb")) #enregistrement des prédictions svm

clf2=pickle.load(open("naivebayes.p","rb")) #chargement du modèle naivebayes
pred_nb=clf2.predict(X_twitter) #calcul des prédictions naive bayes des données twitter
pickle.dump(pred_nb,open("pred_nb.p","wb")) #enregistrement des prédictions naives bayes
