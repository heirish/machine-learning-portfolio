
# coding: utf-8

# In[ ]:
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch import helpers

class ElasticSearchClass(object):
 
    def __init__(self, host, port, user=None, pwd=None):
        self.host = host
        self.port = port
        if user is not None and pwd is not None:
            self.es = Elasticsearch(hosts=[{'host': self.host, 'port': self.port}], http_auth=(user, pwd))
        else:
            self.es = Elasticsearch(hosts=[{'host': self.host, 'port': self.port}])
        
 
    def isValid(self):
        try:
            self.es.ping()
            return True
        except:
            return False
 
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
 
    def search(self, indexName,body=None):
        return self.es.search(index=indexName,body=body)
    
    #scroll size https://github.com/elastic/elasticsearch/issues/18253
    def scrollSearch(self, indexName, batch_size=10, body=None):
        if batch_size is None or batch_size < 10:
            batch_size = 10
        return helpers.scan(self.es,
            query = body, 
            preserve_order = True,
            index = indexName,
            size = batch_size)
    
    def createIndex(self, indexName, body):
        try:
            self.es.indices.delete(index = indexName)
        except elasticsearch.NotFoundError:
            pass
        self.es.indices.create(index = indexName, body = body)
        
    def indexDocument(self, indexName, docType, body, docId=None):
        if docId is not None:
            self.es.index(index = indexName, doc_type = docType, id = docId,
                     body = body)
        else:
            self.es.index(index = indexName, doc_type = docType, body = body)
            
    #https://github.com/elastic/elasticsearch-py/issues/508
    def bulkIndexDocument(self, actions):
        success, _ = helpers.bulk(self.es, actions)
        return success
            
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