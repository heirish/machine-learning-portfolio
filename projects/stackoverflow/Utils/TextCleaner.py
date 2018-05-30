from sklearn.base import TransformerMixin
import multiprocessing

class CleanTextTransformer(TransformerMixin):
    def __init__(self, n_jobs=1, cleanFunc=None):
        self.n_jobs = n_jobs
        if cleanFunc is None:
            self.cleanFunc = self.defaultClean
        else:
            self.cleanFunc = cleanFunc

    def transform(self, X, **transform_params):
        if self.n_jobs > 1:
            # return Parallel(n_jobs=self.n_jobs)(delayed(cleanText)(txt) for txt in X)
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
    def defaultClean(self, text):
        text = text.lower()
        # get rid of newlines
        text = text.strip().replace("\n", " ").replace("\r", " ")
        # delete unicode, or multiprocessing.map will raise encodeerror
        text = text.encode("utf-8", "ignore").decode()
        return text