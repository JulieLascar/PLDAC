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



# Chargement des données Allo ciné
with open('allocine_dataset.pickle', 'rb') as f1:
    OL = pickle.load(f1)

data_train=OL['train_set']
train_review=data_train['review']
train_labels=data_train['polarity']

data_test=OL['test_set']
test_review=data_test['review']
test_labels=data_test['polarity']

print(f"taille des données d'apprentissage :{len(train_review)} \ntaille des données test :{len(test_review)}")

# Les données sont-elles équilibrées?

plt.hist(train_labels, bins=2,rwidth=0.8)
plt.xticks([0, 1])
plt.xlabel("classes")
plt.title("Equilibre des données d'apprentissage")
plt.show()


# pré-traitement 

def preprocess_txt(doc):
    punc = string.punctuation  # recupération de la ponctuation
    punc += '\n\r\t'
    doc = doc.translate(str.maketrans(punc, ' ' * len(punc)))  
    doc = unicodedata.normalize('NFD', doc).encode('ascii', 'ignore').decode("utf-8")
    doc = re.sub('[0-9]+', '', doc)
    doc = doc.lower()
    return doc
    
sw = set(stopwords.words('french'))

stopwords={'film','tout'}
for w in sw:
    stopwords.add(preprocess_txt(w))

# optionnel : visualiser le nuage de points
''' from wordcloud import WordCloud

array_labels_debat=np.array(train_labels)
ind_pos=np.where(array_labels_debat==1)[0]
ind_neg=np.where(array_labels_debat==0)[0]


# Nuage positif
random_train_review=np.random.choice(train_review[ind_pos],5000)
tout=''
for t in random_train_review:
    tout+=t
tout = preprocess_txt(tout)
tout=tout.split()
liste = [word for word in tout if word not in stopwords]
nuage_pos=''
for w in liste:
    nuage_pos += w
    nuage_pos += ' '

    
# Nuage négatif

random_train_review2=np.random.choice(train_review[ind_neg],3000)
tout2=''
for t in random_train_review2:
    tout2+=t
tout2 = preprocess_txt(tout2)
tout2=tout2.split()
liste = [word for word in tout2 if word not in stopwords]
nuage_neg=''
for w in liste:
    nuage_neg += w
    nuage_neg += ' '

print('nuage positif')
wordcloud = WordCloud(background_color = 'white', max_words = 100).generate(nuage_pos)
plt.imshow(wordcloud)
plt.axis("off")
plt.show()
      
print('nuage négatif')
wordcloud = WordCloud(background_color = 'white', max_words = 100).generate(nuage_neg)
plt.imshow(wordcloud)
plt.axis("off")
plt.show() '''



stemmer = FrenchStemmer()

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
    
# Vectorisation des données allociné
vectorizer = StemmedTfidfVectorizer(
    preprocessor=preprocess_txt, 
    stop_words=stopwords, 
    stemmer=stemmer,
    max_features=15000, 
    min_df=2, 
    max_df=0.7, 
    ngram_range=(1,2)
)

X=vectorizer.fit_transform(train_review)
X.toarray()
X = coo_matrix(X)

# Construction de classifieurs naïfs à partir des données vectorisées
train_labels=np.array(train_labels)
clf_svm = svm.LinearSVC()
score = cross_val_score(clf_svm, X, train_labels, cv=5).mean()

clf_nb = nb.MultinomialNB()
score2 = cross_val_score(clf_nb, X, train_labels, cv=5).mean()

print(f"Score par cross validation sur les données allo_ciné : {score}")
print(f"Score par cross validation sur les données allo_ciné : {score2}")

clf_svm.fit(X,train_labels)#construction du modèle
pickle.dump(clf_svm,open("svm.p","wb")) #enregistrement du modèle

clf_nb.fit(X,train_labels)#construction du modèle
pickle.dump(clf_nb,open("naivebayes.p","wb")) #enregistrement du modèle

    