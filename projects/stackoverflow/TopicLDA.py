# ex.: python TopicLDA.py --input_data_dir Data_in --output_data_dir Data_out --max_steps 3 --year 2008


import re
import os
import time
import string
import pyLDAvis
import pyLDAvis.sklearn
import argparse
import spacy
import warnings
import nltk
import pandas as pd
import numpy as np
from zhon import hanzi
from bs4 import BeautifulSoup
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords
from sklearn.feature_extraction.text import CountVectorizer


from Utils import TextProcessor, Tools
import importlib
importlib.reload(TextProcessor)
importlib.reload(Tools)

import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = [16,9]

warnings.filterwarnings(action='once')
warnings.filterwarnings('ignore')


def cleanTextFunc(text):
    # some data will raise NotImplementedError: subclasses of ParserBase must override error()
    try:
        bs = BeautifulSoup(text, "html.parser")
        # code = [s.extract() for s in bs('code')]
        # replace other HTML symbols
        text = bs.get_text()
    except Exception as e:
        # Tools.flushPrint(e)
        pass
    text = text.lower()
    # get rid of newlines
    text = text.strip().replace("\n", " ").replace("\r", " ")
    # replace @xxxx with @mentions
    # here we don't need @mention
    mentionFinder = re.compile(r"@[a-z0-9_]{1,15}", re.IGNORECASE)
    text = mentionFinder.sub("", text)
    # delete numbers
    text = re.sub(r'\w*\d\w*', '', text).strip()
    # delete unicode, or multiprocessing.map will raise encodeerror
    text = text.encode("utf-8", "ignore").decode()
    return text


parser = spacy.load('en', disable=['parser', 'ner'])
punctuations = " ".join(string.punctuation).split(" ") + " ".join(hanzi.punctuation).split(" ")
# only keep nouns and adjectives

# spacy is slower thatn nltk if the data is large when use on linux. might hang the process
# https://github.com/explosion/spaCy/issues/1572
def tokenFuncSpacy(text):
    try:
        tokens = parser(text)
        # only keep nouns and adjectives
        tokens = [tok for tok in tokens if (tok.tag_ in ("NN", "NNS", "NNP", "NNPS", "JJ"))]
        tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
        tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuations)]
        # remove tokens lenth is 1
        tokens = [tok for tok in tokens if (len(tok) > 1)]
        # remove large strings of whitespace
        while "" in tokens:
            tokens.remove("")
        while " " in tokens:
            tokens.remove(" ")
        while "\n" in tokens:
            tokens.remove("\n")
        while "\n\n" in tokens:
            tokens.remove("\n\n")
    except Exception as e:
        Tools.flushPrint(e)
        Tools.flushPrint(text)
        tokens = []
    return tokens


# pip install nltk
# import nltk
# nltk.download("all")
def tokenFuncNltk(text):
    try:
        tokens = nltk.word_tokenize(text)
        tags = nltk.pos_tag(tokens)
        tokens = [word for word, pos in tags if (pos in ("NN", "NNS", "NNP", "NNPS", "JJ"))]
        tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuations)]
        # remove tokens lenth is 1
        tokens = [tok for tok in tokens if (len(tok) > 1)]
        # remove large strings of whitespace
        while "" in tokens:
            tokens.remove("")
        while " " in tokens:
            tokens.remove(" ")
        while "\n" in tokens:
            tokens.remove("\n")
        while "\n\n" in tokens:
            tokens.remove("\n\n")
    except Exception as e:
        Tools.flushPrint(e)
        Tools.flushPrint(text)
        tokens = []

    return tokens


def trainLDA(data, n_topics, max_iterations):
    lda = LatentDirichletAllocation(n_components=n_topics,
                                    max_iter=max_iterations,
                                    learning_method='online',
                                    random_state=125,
                                    evaluate_every=10#,
                                    # #learning_decay=0.7
                                    )
    lda.fit(data)
    return lda


def trainLDAGridSearch(data, search_params):
    # Init the Model
    lda = LatentDirichletAllocation()
    # Init Grid Search Class
    model = GridSearchCV(lda, param_grid=search_params)
    # Do the Grid Search
    model.fit(data)

    # Best Model
    Tools.flushPrint("Best Model's Params: ", model.best_params_)
    best_lda_model = model.best_estimator_
    return best_lda_model


def getLDATopWords(lda, feature_names, n_top):
    topic_list = []
    for topic_idx, topic in enumerate(lda.components_):
        top_words = " ".join([feature_names[i]
                              for i in topic.argsort()[:-n_top- 1:-1]])
        topic_list.append([topic_idx, top_words])
    return topic_list


def visDocTopicDist(doctopic):
    # N documents, K topics
    N, K = doctopic.shape
    ind = np.arange(N)
    width = 0.5
    height_cumulative = np.zeros(N)
    plots=[]
    for k in range(K):
        color = plt.cm.coolwarm(k/K, 1)
        if k == 0:
            p = plt.bar(ind, doctopic[:, k], width, color=color)
        else:
            p = plt.bar(ind, doctopic[:, k], width, bottom=height_cumulative, color=color)
        height_cumulative += doctopic[:, k]
        plots.append(p)
    plt.ylim(0, 1)
    plt.ylabel('Topics')
    plt.title('Topics in docs')
    plt.xticks(ind+width/2, [n for n in range(N)])
    plt.yticks(np.arange(0, 1, 10))
    topic_labels=['Topic #{}'.format(k) for k in range(K)]
    plt.legend([p[0] for p in plots], topic_labels)
    plt.show()


def visLDAIPython(model, data, vectorizer, ip, port):
    pyLDAvis.enable_notebook()
    # https://github.com/bmabey/pyLDAvis/issues/69
    visData = pyLDAvis.sklearn.prepare(model, data, vectorizer, mds='mmds', sort_topics=False)
    pyLDAvis.show(visData,  ip=ip, port=port)


def visLDA(model, data, vectorizer, ip, port):
    # https://github.com/bmabey/pyLDAvis/issues/69
    visData = pyLDAvis.sklearn.prepare(model, data, vectorizer, mds='mmds', sort_topics=False)
    pyLDAvis.show(visData,  ip=ip, port=port)


def parseParameters():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--max_steps',
        type=int,
        default=100,
        help='Number of steps to run trainer.'
    )
    parser.add_argument(
        '--input_data_dir',
        type=str,
        default='./Data_in',
        help='Directory to put the input data.'
    )
    parser.add_argument(
        '--output_data_dir',
        type=str,
        default='./Data_out',
        help='Directory to put the log data.'
    )
    parser.add_argument(
        '--year',
        type=int,
        default=2008,
        help='year of data.'
    )

    return parser.parse_known_args()


if __name__ == "__main__":
    FLAGS, unparsed = parseParameters()
    if unparsed:
        Tools.flushPrint("unparsed parameters: ", unparsed)
    max_iterations = FLAGS.max_steps
    input_data_dir = FLAGS.input_data_dir
    output_data_dir = FLAGS.output_data_dir
    year = FLAGS.year

    df = pd.read_csv(os.path.join(FLAGS.input_data_dir, "Posts_{}.csv".format(year)), encoding="utf-8")
    data = df["body"].values
    # heirish test
    # data = data[:100]

    cleaner = TextProcessor.TextProcessTransformer(cleanTextFunc, n_jobs=8, n_chunks=2)
    cleaned_data = cleaner.fit_transform(data)
    Tools.flushPrint(cleaned_data[:10])
    del data

    # spacy is slower thatn nltk if the data is large when use on linux. might hang the process
    # https://github.com/explosion/spaCy/issues/1572
    # tokenizer = TextProcessor.TextProcessTransformer(tokenFuncSpacy, n_jobs=8, n_chunks=2)

    start_time = time.time()
    tokenizer = TextProcessor.TextProcessTransformer(tokenFuncNltk, n_jobs=8, n_chunks=2)
    tokenized_data = tokenizer.fit_transform(cleaned_data)
    Tools.flushPrint(tokenized_data[:10])
    del cleaned_data
    end_time = time.time()
    Tools.flushPrint("tokenized in {} seconds".format(end_time - start_time))

    start_time = time.time()
    vectorizer = CountVectorizer(
        # so we can pass it strings
        input='content',
        # turn off preprocessing of strings to avoid corrupting our keys
        lowercase=False,
        preprocessor=lambda x: x,
        # use our token dictionary
        tokenizer=lambda x: x,
        min_df=3,
        max_df=0.8,
        max_features=20000)
    vectorized_data = vectorizer.fit_transform(tokenized_data)
    # Tools.flushPrint(vectorized_data[:10])
    del tokenized_data
    end_time = time.time()
    Tools.flushPrint("vectorized in {} seconds".format(end_time - start_time))

    start_time = time.time()
    n_topics = 50
    # lda = trainLDA(vectorized_data, n_topics, max_iterations)
    search_params = {'n_components': [n_topics], 'learning_decay': [.7, .9], 'max_iter': [100, 200]}
    lda = trainLDAGridSearch(vectorized_data, search_params)
    Tools.flushPrint(lda)
    try:
        Tools.dillDump(os.path.join(output_data_dir, "lda_{}.pkl".format(year)), lda)
    except:
        pass

    feature_names = vectorizer.get_feature_names()
    topic_list = getLDATopWords(lda, feature_names, 20)
    train_gamma = lda.transform(vectorized_data)
    Tools.flushPrint("train_gamma:{}".format(train_gamma.shape))
    train_perplexity = lda.perplexity(vectorized_data)
    end_time = time.time()
    Tools.flushPrint("Trained LDA in {} Seconds, preplexity {}\n"
          .format(end_time - start_time, train_perplexity))

    # get document_topic_distribution
    # visDocTopicDist(train_gamma[:10])
    # Tools.flushPrint(train_gamma.shape)
    # Tools.flushPrint(train_gamma[0])

    # save result to csv
    df_topics = pd.DataFrame(topic_list, columns=["topic_index", "topic_words"])
    df_topics.to_csv(os.path.join(output_data_dir, "stackoverflow_topics_{}.csv".format(year)),
                     sep=",", encoding="utf-8", index=False)

    df_doc_topics = pd.DataFrame(train_gamma, columns=["topic #" + str(i) for i in range(n_topics)])
    df_doc_topics['idlist'] = df["docID"]
    df_doc_topics.to_csv(os.path.join(output_data_dir, "stackoverflow_topic_coverage_{}.csv".format(year)),
                         sep=',', encoding='utf-8', index=False)

    visLDA(lda, vectorized_data, vectorizer, Tools.getIP(), 8000+int(year))
