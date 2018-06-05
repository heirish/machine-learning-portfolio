import os
import time
import argparse
import pyLDAvis
import pyLDAvis.sklearn
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

from Utils import Tools, TextProcessor
import importlib
importlib.reload(Tools)
importlib.reload(TextProcessor)


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
        '--type_name',
        type=str,
        default='tag',
        help='Data type to train on, can be tags or title'
    )

    return parser.parse_known_args()


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


def getLDATopWords(lda, feature_names, n_top):
    topic_list = []
    for topic_idx, topic in enumerate(lda.components_):
        top_words = " ".join([feature_names[i]
                              for i in topic.argsort()[:-n_top - 1:-1]])
        topic_list.append([topic_idx, top_words])
    return topic_list


def visLDA(model, data, vectorizer, ip, port):
    # https://github.com/bmabey/pyLDAvis/issues/69
    visData = pyLDAvis.sklearn.prepare(model, data, vectorizer, mds='mmds', sort_topics=False)
    pyLDAvis.show(visData,  ip=ip, port=port)

if __name__ == "__main__":
    FLAGS, unparsed = parseParameters()
    if unparsed:
        Tools.flushPrint("unparsed parameters: {}".format(unparsed))
    max_iterations = FLAGS.max_steps
    input_data_dir = FLAGS.input_data_dir
    output_data_dir = FLAGS.output_data_dir
    type_name = FLAGS.type_name

    if type_name == 'tag':
        df = pd.read_csv(os.path.join(FLAGS.input_data_dir, "tags.csv"))
        data = df["tag"].values
    elif type_name == "title":
        df = pd.read_csv(os.path.join(FLAGS.input_data_dir, "titles.csv"))
        data = df["title"].values
    else:
        raise ValueError("invalid type_name")
    Tools.flushPrint(data.shape)
    # heirish test
    # data = data[:1000]

    start_time = time.time()
    tokenizer = TextProcessor.TextProcessTransformer(TextProcessor.defaultTokenFunc, n_jobs=8, n_chunks=20)
    tokenized_data = tokenizer.fit_transform(data)
    Tools.flushPrint(tokenized_data[:10])
    del data
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
    lda = trainLDA(vectorized_data, n_topics, max_iterations)
    Tools.flushPrint(lda)
    try:
        Tools.dillDump(os.path.join(output_data_dir, "lda_tag.pkl"), lda)
    except:
        pass
    end_time = time.time()
    Tools.flushPrint("Trained LDA in {} Seconds".format(end_time - start_time))

    feature_names = vectorizer.get_feature_names()
    topic_list = getLDATopWords(lda, feature_names, 20)
    train_gamma = lda.transform(vectorized_data)
    train_perplexity = lda.perplexity(vectorized_data)
    Tools.flushPrint("train_gamma:{}, perplexity {}".format(train_gamma.shape, train_perplexity))

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

    visLDA(lda, vectorized_data, vectorizer, Tools.getIP(), 10020)
