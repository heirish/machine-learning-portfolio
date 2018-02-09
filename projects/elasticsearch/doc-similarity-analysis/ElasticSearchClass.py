
# coding: utf-8

# In[ ]:
import elasticsearch
from elasticsearch import Elasticsearch

class ElasticSearchClass(object):
 
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connect()
 
    def connect(self):
        self.es = Elasticsearch(hosts=[{'host': self.host, 'port': self.port}])
 
    def count(self, indexName):
        """
        :param indexname:
        :return: 统计index总数
        """
        return self.es.count(index=indexName)
 
    def delete(self, indexName, docType, id):
        """
        :param indexname:
        :param doc_type:
        :param id:
        :return: 删除index中具体的一条
        """
        self.es.delete(index=indexName, doc_type=docType, id=id)
 
    def get(self, indexName, docType, id):
        return self.es.get(index=indexName,doc_type=docType, id=id)
 
    def search(self, indexName, size=10):
        try:
            return self.es.search(index=indexName, size=size, sort="@timestamp:desc")
        except Exception as err:
            print(err)
    
    def createIndex(self, indexName, body):
        try:
            self.es.indices.delete(index = indexName)
        except elasticsearch.NotFoundError:
            pass
        self.es.indices.create(index = indexName, body = body)
        
    def indexDocument(self, indexName, docType, id, body):
        try:
            self.es.index(index = indexName, doc_type = docType, id = id,
                     body = body)
        except Exception as e:
            print(e)
            
    def moreLikeThis(self, indexName, docType, id, mltFields, search_size=2, min_term_freq=1, min_doc_freq=1):
        return self.es.search(body={"size":search_size,
            "query": {
                               "more_like_this" : {
                                   "fields" : mltFields,
                                   "like" : [
                                    {
                                        "_index" : indexName,
                                        "_type" : docType,
                                        "_id" : id
                                    }],
                                   "min_term_freq" : min_term_freq,
                                   "min_doc_freq" : min_doc_freq
                               }
                           }})
    
    def termVector(self, indexName, docType, id):
        return self.es.termvectors(indexName, docType, id)
        '''
         return self.es.termvectors(body={
            'docs':[
                {
                    "_index" : indexName,
                    "_type" : docType,
                    "_id" : id
                }
                ]})
          '''

