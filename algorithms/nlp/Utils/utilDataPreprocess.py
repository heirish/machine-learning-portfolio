from joblib import Parallel, delayed
import multiprocessing
import spacy
from sklearn.feature_extraction.text import CountVectorizer 
from sklearn.pipeline import Pipeline
from sklearn.base import TransformerMixin 
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords 
import string
import time

###########create data clearner
     
class CleanTextTransformer(TransformerMixin):
    def __init__(self, n_jobs=1, cleanFunc=None):
        self.n_jobs=n_jobs
        if cleanFunc is None:
            self.cleanFunc = self.defaultClean
        else:
            self.cleanFunc = cleanFunc
            
    def transform(self, X, **transform_params):
        if self.n_jobs > 1:
            #return Parallel(n_jobs=self.n_jobs)(delayed(cleanText)(txt) for txt in X)
            pool = multiprocessing.Pool(processes=self.n_jobs)
            results = pool.map(self.cleanFunc, X)
            pool.close()
            pool.join()
            return results
        else:
            return [self.cleanFunc(txt) for txt in X]
        
    def fit(self, X, y=None, **fit_params):
        return self
    
    def get_params(self, deep=True):
        return {}

    # A custom function to clean the text before sending it into the vectorizer
    def defaultClean(self,text):
        text = text.lower()
        # get rid of newlines
        text = text.strip().replace("\n", " ").replace("\r", " ")
        # delete unicode, or multiprocessing.map will raise encodeerror
        text = text.encode("utf-8", "ignore").decode()
        return text


############create tokenizer
punctuations = " ".join(string.punctuation).split(" ")
parser = spacy.load('en', disable=['parser', 'ner'])
#Custom transformer using spaCy
class VectorizationTransformer(TransformerMixin):
    def __init__(self, n_token_jobs=1, n_token_chunks =1, tokenFunc=None, vectorizer = None):
        self.n_token_jobs = n_token_jobs
        self.n_token_chunks = n_token_chunks
        self.tokenFunc = tokenFunc
            
        if vectorizer is None:
            #https://stackoverflow.com/questions/35867484/pass-tokens-to-countvectorizer
            self.vectorizer = CountVectorizer(
                # so we can pass it strings
                input='content',
                # turn off preprocessing of strings to avoid corrupting our keys
                lowercase=False,
                preprocessor=lambda x: x,
                # use our token dictionary
                tokenizer=lambda x:x)
        else:
            self.vectorizer = vectorizer
            
    def transform(self, X, **transform_params):
        if self.tokenFunc is not None:
            tokenized_data = self.tokenFunc(X, self.n_token_jobs, self.n_token_chunks)
        else:
            tokenized_data = X
        vectorized_data = self.vectorizer.fit_transform(tokenized_data)
        return tokenized_data, vectorized_data, self.vectorizer
    
    def fit(self, X, y=None, **fit_params):
        return self
    
    def get_params(self, deep=True):
        return {}
    
    def defaultTokenFunc(self, X, n_token_jobs, n_token_chunks):
        tokenized_data = []
        chunk_size = int(math.ceil(len(X) / n_token_chunks))
        if n_token_jobs>1:
            pool = multiprocessing.Pool(n_token_jobs)
            for i in range(n_token_chunks):
                tokenized_data_tmp = pool.map(defaultTokenizer, X[chunk_size*i:chunk_size*(i+1)])
                tokenized_data.extend(tokenized_data_tmp)
            pool.close()
            pool.join()
        else:
            for i in range(n_token_chunks):
                tokenized_data_tmp = [self.defaultTokenizer(x) for x in X[chunk_size*i:chunk_size*(i+1)]]
                tokenized_data.extend(tokenized_data_tmp)
        return tokenized_data

#Create spacy tokenizer that parses a sentence and generates tokens
#these can also be replaced by word vectors 
# List of symbols we don't care about
def defaultTokenizer(self,sentence):
    tokens = parser(sentence)
    tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
    tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuations)]
    return tokens
    
##########Create preprocess pipline and run
def preProcessData(X_train, n_jobs=1, max_features=None, tokenizer = None,):
    #create vectorizer object to generate feature vectors, we will use custom spacy’s tokenizer
    #vectorizer = TfidfVectorizer(tokenizer = tokenizeText)
    #svd = TruncatedSVD(2)
    #normalizer = Normalizer(copy=False)
    #removed any word that appeared in more than 70% of documents.
    #removed any word that appeared in less than 5 documents
    if tokenizer is None:
        tokenizer = defaultTokenizer
    vectorizer = CountVectorizer(tokenizer = tokenizer, min_df=5, max_df = 0.6, max_features=max_features)
    start_time = time.time()
    pipe_preprocess = Pipeline([("cleaner", CleanTextTransformer(n_jobs=n_jobs)),
                 ("vectorizer", vectorizer)])
    X_train_preprocess = pipe_preprocess.fit_transform(X_train)
    end_time = time.time()
    print("Preprocess done in {} Seconds, n_jobs={}".format(end_time - start_time, n_jobs))
    return X_train_preprocess, vectorizer