from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = [16,9]
import pyLDAvis
import pyLDAvis.sklearn
import numpy as np

def trainLDA(data, n_topics = 10, max_iter=100, batch_size=64, n_jobs=-1):
    lda = LatentDirichletAllocation(n_topics=n_topics, n_jobs=n_jobs,
                                max_iter=max_iter,
                                learning_method='online',
                                batch_size=batch_size,
                                random_state=125)

    lda.fit(data)
    return lda

def get_top_words(model, feature_names, n_top_words):
    topic_list=[]
    for topic_idx, topic in enumerate(model.components_):
        top_words=" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]])
        topic_list.append([topic_idx, top_words])
    return topic_list
    
##visualize doc_topic_distr
#https://de.dariah.eu/tatom/topic_model_visualization.html
def visDocTopicDist(doctopic):
    #N documents, K topics
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
    plt.ylim(0,1)
    plt.ylabel('Topics')
    plt.title('Topics in docs')
    plt.xticks(ind+width/2, [n for n in range(N)])
    plt.yticks(np.arange(0,1,10))
    topic_labels=['Topic #{}'.format(k) for k in range(K)]
    plt.legend([p[0] for p in plots], topic_labels)
    plt.show()
    
def visLDA(model, data, vectorizer, ip, port):
    pyLDAvis.enable_notebook()
    #https://github.com/bmabey/pyLDAvis/issues/69
    visData = pyLDAvis.sklearn.prepare(model, data, vectorizer, mds='mmds')
    #pyLDAvis.show(visData,  ip="127.0.0.1", port=8889)
    pyLDAvis.show(visData,  ip=ip, port=port)