import string
import spacy
import math
import multiprocessing
from sklearn.base import TransformerMixin
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords

############create tokenizer
punctuations = " ".join(string.punctuation).split(" ")
parser = spacy.load('en', disable=['parser', 'ner'])


# A custom function to clean the text before sending it into the vectorizer
def defaultClean(self, text):
    text = text.lower()
    # get rid of newlines
    text = text.strip().replace("\n", " ").replace("\r", " ")
    # delete unicode, or multiprocessing.map will raise encodeerror
    text = text.encode("utf-8", "ignore").decode()
    return text


# Create spacy tokenizer that parses a sentence and generates tokens
# these can also be replaced by word vectors
# List of symbols we don't care about
def defaultTokenFunc(self, sentence):
    tokens = parser(sentence)
    tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
    tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuations)]
    return tokens


class TextProcessTransformer(TransformerMixin):
    def __init__(self, processFunc, n_jobs=1, n_chunks=1):
        self.n_jobs = n_jobs
        self.n_chunks = n_chunks
        if processFunc is None:
            raise ValueError("you must feed a precessFunc, if no idea, you can try the default functions,"
                             "such as defaultClean, defaultToken, etc.")
        else:
            self.processFunc = processFunc

    def transform(self, X, **transform_params):
        results = []
        chunk_size = int(math.ceil(len(X) / self.n_chunks))
        if self.n_jobs > 1:
            pool = multiprocessing.Pool(self.n_jobs)
            for i in range(self.n_chunks):
                data_tmp = pool.map(self.processFunc, X[chunk_size * i:chunk_size * (i + 1)])
                results.extend(data_tmp)
            pool.close()
            pool.join()
        else:
            for i in range(self.n_chunks):
                data_tmp = [self.processFunc(x) for x in X[chunk_size * i:chunk_size * (i + 1)]]
                results.extend(data_tmp)
        return results

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}


class DenseTransformer(TransformerMixin):
    def transform(self, X, y=None, **fit_params):
        return X.todense()

    def fit_transform(self, X, y=None, **fit_params):
        self.fit(X, y, **fit_params)
        return self.transform(X)

    def fit(self, X, y=None, **fit_params):
        return self