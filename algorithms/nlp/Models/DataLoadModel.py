# coding: utf-8

# In[ ]:
from sklearn.datasets import fetch_20newsgroups
from Models import ElasticSearchClass


def iterLoadStackoverflowFromES(maxCount=-1):
    esUtil = ElasticSearchClass.ElasticSearchClass("192.168.18.187", 9201)
    dsl = '''
    {
    "_source":["body"],
    "query":{
        "bool":{
            "must":{
                "match":{"posttypeid":1}}
            }
        }
    }
    '''
    res = esUtil.scrollSearch(indexName="stackoverflow", body=dsl)
    print(res)
    count = 0
    data = []
    #chooseUtil = RandomChoose.RandomChoose(0.001)
    for doc in res:
        #if chooseUtil.choose() == False:
            #continue
        if maxCount > 0 and count >= maxCount:
            break
        count += 1
        data.append([doc['_id'], doc['_source']['body']])
        #print(doc['_id'], doc['_source']['body'])
    return data

def loadStackoverflowFromES():
    esUtil = ElasticSearchClass.ElasticSearchClass("192.168.18.187", 9201)
    dsl = '''
    {
    "_source":["title", "body"],
    "query":{
        "bool":{
            "must":{
                "match":{"posttypeid":1}}
            }
        },
    "size":1
    }
    '''
    res = esUtil.search(indexName="stackoverflow", body=dsl)
    for doc in res['hits']['hits']:
         print("%s) %s" % (doc['_id'], doc['_source']))
            
def load20NewsGroups():
    # #############################################################################
    # Load some categories from the training set
    categories = [
        'alt.atheism',
        'talk.religion.misc',
        'comp.graphics',
        'sci.space',
     ]
    dataset = fetch_20newsgroups(subset='all', categories=categories,
                             shuffle=True, random_state=42)
    print("%d documents" % len(dataset.data))
    print("%d categories" % len(dataset.target_names))
    return dataset.data
