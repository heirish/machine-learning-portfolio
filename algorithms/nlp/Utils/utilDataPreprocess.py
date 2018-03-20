from joblib import Parallel, delayed
import multiprocessing
import spacy
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer 
from sklearn.pipeline import Pipeline
from sklearn.base import TransformerMixin 
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords 
import re
import string
import time

###########create data clearner

#Custom transformer using spaCy 
class CleanTextTransformer(TransformerMixin):
    def __init__(self, n_jobs=1):
        self.n_jobs=n_jobs
    def transform(self, X, **transform_params):
        if self.n_jobs > 1:
            #return Parallel(n_jobs=self.n_jobs)(delayed(cleanText)(txt) for txt in X)
            pool = multiprocessing.Pool(processes=self.n_jobs)
            results = pool.map(cleanText, X)
            pool.close()
            pool.join()
            return results
        else:
            return [cleanText(txt) for txt in X]
    def fit(self, X, y=None, **fit_params):
        return self
    def get_params(self, deep=True):
        return {}

# A custom function to clean the text before sending it into the vectorizer
def cleanText(text):
   #some data will raise NotImplementedError: subclasses of ParserBase must override error()
    try:
        bs = BeautifulSoup(text, "html.parser")
        #code = [s.extract() for s in bs('code')]
        # replace other HTML symbols
        text = bs.get_text()
    except Exception as e:
        #print(e)
        pass
    text = text.lower()
    # get rid of newlines
    text = text.strip().replace("\n", " ").replace("\r", " ")
    # replace @xxxx with @mentions
    mentionFinder = re.compile(r"@[a-z0-9_]{1,15}", re.IGNORECASE)
    text = mentionFinder.sub("@mention", text)
    # here we don't need @mention
    text = re.sub("@mention", '', text).strip()
    # delete numbers
    text = re.sub(r'\w*\d\w*', '', text).strip()
    return text

############create tokenizer

#Create spacy tokenizer that parses a sentence and generates tokens
#these can also be replaced by word vectors 
# List of symbols we don't care about
punctuations = " ".join(string.punctuation).split(" ") + ["-----", "---", "...", "“", "”", "'ve", "--", "//", "div"]
parser = spacy.load('en')
def tokenizeText(sentence):
    tokens = parser(sentence)
    #only keep nouns
    tokens = [tok for tok in tokens if (tok.tag_ in ("NN", "NNS", "NNP", "NNPS", "JJ"))]
    tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
    tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuations)]
    #remove tokens lenth is 1
    tokens = [tok for tok in tokens if (len(tok)>1)]
    # remove large strings of whitespace
    while "" in tokens:
        tokens.remove("")
    while " " in tokens:
        tokens.remove(" ")
    while "\n" in tokens:
        tokens.remove("\n")
    while "\n\n" in tokens:
        tokens.remove("\n\n")
    return tokens

def countvectorizeData(data, min_df=5, max_df = 0.6, max_features=None):
    start_time = time.time()
    vectorizer = CountVectorizer(tokenizer = tokenizeText, min_df=min_df, max_df = max_df, max_features=max_features)
    vectorized_data = vectorizer.fit_transform(data)
    end_time = time.time()
    print("vectorize done in {} Seconds".format(end_time - start_time))
    return vectorized_data, vectorizer

##########Create preprocess pipline and run
def preProcessData(X_train, n_jobs=1, max_features=None):
    #create vectorizer object to generate feature vectors, we will use custom spacy’s tokenizer
    #vectorizer = TfidfVectorizer(tokenizer = tokenizeText)
    #svd = TruncatedSVD(2)
    #normalizer = Normalizer(copy=False)
    #removed any word that appeared in more than 70% of documents.
    #removed any word that appeared in less than 5 documents
    cleaner = CleanTextTransformer(n_jobs=n_jobs)
    vectorizer = CountVectorizer(tokenizer = tokenizeText, min_df=5, max_df = 0.6, max_features=max_features)
    start_time = time.time()
    pipe_preprocess = Pipeline([("cleaner", cleaner),
                 ("vectorizer", vectorizer)])
    X_train_preprocess = pipe_preprocess.fit_transform(X_train)
    end_time = time.time()
    print("Preprocess done in {} Seconds, n_jobs={}".format(end_time - start_time, n_jobs))
    return X_train_preprocess, vectorizer