# coding: utf-8

# In[ ]:
from sklearn.datasets import fetch_20newsgroups
from Models import ElasticSearchClass
import xml.etree.ElementTree as ET

def loadStackoverflowFromXML(XMLFile, maxCount = -1):
    context = ET.iterparse(XMLFile, events=("start", "end"))
    #turn it into an iterator
    context = iter(context)
    #get the root element
    event, root = next(context)
    count = 0 
    data = []
    for event, elem in context:
        if maxCount > 0 and count > maxCount:
            break
        if event == "end" and elem.tag == "row":
            values=dict()
            for key in elem.attrib.keys():
                if key.lower() == "body" or key.lower() == "posttypeid":
                    values[key.lower()] = elem.attrib.get(key)
                elif key.lower() == "id": # change field name to docID
                    values["docId"] = elem.attrib.get(key)
                else:
                    #values[key.lower()] = elem.attrib.get(key)
                    continue
            elem.clear()
            if values["posttypeid"] != "1": #only retrive questions
                continue
            count += 1
            data.append([values["docId"], values["body"]])
        root.clear()
    print("Parse XML [%s]Done, total [%d] records!" % (XMLFile, count))
    return data

def iterLoadStackoverflowFromES(maxCount=10000):
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
        if count >= maxCount:
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