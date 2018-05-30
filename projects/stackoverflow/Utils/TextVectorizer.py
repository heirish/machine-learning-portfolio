import string
import spacy
import math
import multiprocessing
from sklearn.base import TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords

############create tokenizer
punctuations = " ".join(string.punctuation).split(" ")
parser = spacy.load('en', disable=['parser', 'ner'])

# Custom transformer using spaCy
class VectorizationTransformer(TransformerMixin):
    def __init__(self, n_token_jobs=1, n_token_chunks=1, tokenFunc=None, vectorizer=None):
        self.n_token_jobs = n_token_jobs
        self.n_token_chunks = n_token_chunks
        self.tokenFunc = tokenFunc

        if vectorizer is None:
            # https://stackoverflow.com/questions/35867484/pass-tokens-to-countvectorizer
            self.vectorizer = CountVectorizer(
                # so we can pass it strings
                input='content',
                # turn off preprocessing of strings to avoid corrupting our keys
                lowercase=False,
                preprocessor=lambda x: x,
                # use our token dictionary
                tokenizer=lambda x: x)
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
        if n_token_jobs > 1:
            pool = multiprocessing.Pool(n_token_jobs)
            for i in range(n_token_chunks):
                tokenized_data_tmp = pool.map(defaultTokenizer, X[chunk_size * i:chunk_size * (i + 1)])
                tokenized_data.extend(tokenized_data_tmp)
            pool.close()
            pool.join()
        else:
            for i in range(n_token_chunks):
                tokenized_data_tmp = [defaultTokenizer(x) for x in X[chunk_size * i:chunk_size * (i + 1)]]
                tokenized_data.extend(tokenized_data_tmp)
        return tokenized_data


class DenseTransformer(TransformerMixin):
    def transform(self, X, y=None, **fit_params):
        return X.todense()

    def fit_transform(self, X, y=None, **fit_params):
        self.fit(X, y, **fit_params)
        return self.transform(X)

    def fit(self, X, y=None, **fit_params):
        return self


# Create spacy tokenizer that parses a sentence and generates tokens
# these can also be replaced by word vectors
# List of symbols we don't care about
def defaultTokenizer(self, sentence):
    tokens = parser(sentence)
    tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
    tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuations)]
    return tokens