import pandas as pd
from datetime import datetime, timedelta
import time
from urllib import parse
import requests
from urllib.request import urlretrieve
import json
import re
import hashlib
import logging

from Models import ElasticSearchClass
import importlib
importlib.reload(ElasticSearchClass)

pd.options.display.max_colwidth = 512

def acceptQuery(query, instance):
    if instance is None:
        return True
    if query is None:
        return False
    
    #other filters
        
    return True 
        
def exists(data, record):
    if data is None:
        return False
    if record is None:
        raise ValueError("record None")
    
    return record in data

def isJavaStacktrace(text):
    if re.search(r"(at)?.*\(.*.java:\d+\)", text):
        return True
    else:
        return False
        

def isP(doc, hosts, percolatorIndex):
    dsl = ""
    try:
        esUtil = ElasticSearchClass.ElasticSearchClass(hosts)
        doc_json = json.dumps(doc["_source"])
        dsl = """
        {{
            "size":0,
            "query": {{
                "bool": {{
                "must": [
                    {{
                       "percolate": {{
                       "field": "query",
                       "document_type": "doctype",
                       "document": {doc}
                       }}
                    }}
                 ]
              }}
           }} 
        }}""".format(doc=doc_json)
        res = esUtil.search(percolatorIndex, dsl)
        if res['hits']['total'] > 0:
            return True
    except Exception as e:
        #print(e)
        #print(dsl)
        pass
    
    return False

def formatResult(doc):
    try: 
        body = doc['_source']['body']
        #max accept body lenth is 10*2014
        if (len(body.strip()) == 0):
            return None
        if (len(body) > 10*1024):
            return None
        if isJavaStacktrace(body):
            return None
    
        return [doc['_index'], doc['_type'], doc['_id'], str(doc['_source']['body'])]
    except Exception as e:
        return None
    
def loadPercolatorQueries(indexName, instance, hosts, maxCount=-1):
    if indexName is None or hosts is None:
        raise ValueError("indexName, esUtil invalid.")
    
    esUtil = ElasticSearchClass.ElasticSearchClass(hosts)
    res = esUtil.scrollSearch(indexName=indexName)
    count = 0
    data = []
    for doc in res:
        if maxCount > 0 and count >= maxCount:
            break
        query = str(doc['_source']['query'])
        if acceptQuery(query, instance):
            data.append([doc['_id'], query])
            count += 1
    return data

#retrieve logs to be labedled to 1
def retrievePFromES(queryString, hosts, projectName, 
                   maxCount=200, startDate=None, toleranceDays=30):
    if hosts is None or projectName is None:
        raise ValueError("hosts, projectName invalid.")
        
    dateformat="%Y%m%d"
    if startDate is None:
        startDate =  datetime.datetime.now().strftime(dateformat)
    
    count = 0
    dataRetrieved = []
    data_body = set()
    for i in range(toleranceDays):
        try:
            dataDate = datetime.strptime(startDate, dateformat) - timedelta(days=i)
            aliasName = "log-" + dataDate.strftime(dateformat) + "-" + projectName
            requestString = hosts + "/" + aliasName + "/_search?q=" + parse.quote(queryString) \
                   + "&size=" + str(maxCount*2)
            #print(requestString)
            #response = urlretrieve(requestString)
            response = requests.get(requestString, timeout=5*60)
            results = json.loads(response.text)
            for doc in results['hits']['hits']:
                result = formatResult(doc)
                if result is None:
                    continue
                    
                body_md5 = hashlib.md5(doc['_source']['body'].encode('utf-8')).hexdigest()
                if exists(data_body, body_md5):
                    continue
                data_body.add(body_md5)
                
                dataRetrieved.append(result)
                count += 1
                if maxCount > 0 and count >= maxCount:
                    return dataRetrieved
        except Exception as e:
            #print(e)
            pass
            
    return dataRetrieved

#retrieve logs to be labedled to 0
def retrieveNFromeES(percolatorIndex, hosts, projectName, 
                     maxCountPerDay=100, startDate=None, toleranceDays=30, debug=False):
    dateformat="%Y%m%d"
    if startDate is None:
        startDate =  datetime.datetime.now().strftime(dateformat)
    
    dataRetrieved = []
    data_body = set()
    maxRetrievePerDay = maxCountPerDay*10
    for i in range(toleranceDays):
        dataDate = datetime.strptime(startDate, dateformat) - timedelta(days=i)
        aliasName = "log-" + dataDate.strftime(dateformat) + "-" + projectName
        alreadyReturned = 0
        count = 0
        while alreadyReturned < maxRetrievePerDay and count < maxCountPerDay:
            try:
                requestString = hosts + "/" + aliasName + "/_search?q=" \
                          + "&from=" + str(alreadyReturned) + "&size=" + str(maxCountPerDay)
                #print(requestString)
                #response = urlretrieve(requestString)
                response = requests.get(requestString, timeout=5*60)
                results = json.loads(response.text)
                
                if debug:
                    logging.debug(requestString)
                
                if len(results['hits']['hits']) == 0: #No data
                    break
                for doc in results['hits']['hits']:
                    alreadyReturned += 1
                    result = formatResult(doc)
                    if result is None:
                        continue
                        
                    body_md5 = hashlib.md5(doc['_source']['body'].encode('utf-8')).hexdigest()
                    if exists(data_body, body_md5):
                        continue
                    data_body.add(body_md5)
                    
                    if isP(doc, hosts, percolatorIndex):
                        continue 
                    
                    dataRetrieved.append(result)
                    count += 1
                    if debug:
                        logging.debug("appended:", count, maxCountPerDay)
                    if maxCountPerDay > 0 and count >= maxCountPerDay:
                        break
            except Exception as e:
                alreadyReturned += maxCountPerDay #exception happened, try next retrieve
                #print(e)
                pass
            
    return dataRetrieved

def loadPlogs(instance, instanceConf, startDate):
    index_name = instanceConf['single_alert']
    host = instanceConf['host']
    queries = loadPercolatorQueries(index_name, instance, host)
    df_queries = pd.DataFrame(queries, columns=['ruleid', 'query', 'projects'])
    df_queries.to_csv("./{}-{}.csv".format(index_name, instance), sep=',', encoding='utf-8', index=False)
    
    df_Plogs = pd.DataFrame()
    for index, row in df_queries.iterrows():
        queryString = row['query']
        projectName = row['projects'].lstrip("['").rstrip("']")
        data_tmp = retrievePFromES(queryString, host, projectName, 100, startDate)
        df_log_tmp = pd.DataFrame(data_tmp, columns=['index', 'type', 'id', 'routing', 'body'])
        df_log_tmp['ruleid'] = row['ruleid']
        df_Plogs = df_Plogs.append(df_log_tmp, ignore_index=True)
        #for test
        #print("{} query done, records {}".format(row['ruleid'], len(data_tmp)))
        #if df_Plogs.shape[0] >= 1:
        #    break;
    df_Plogs.to_csv("./{}-{}-Plogs.csv".format(index_name, instance), sep=",", encoding="utf-8", index=False)


def loadNlogs(instance, instanceConf, startDate):
    index_name = instanceConf['single_alert']
    host = instanceConf['host']
    project_file = instanceConf['project_file']
    df_projects = pd.read_csv(project_file, sep=" ", header=None, names=["project"])
    
    df_Nlogs = pd.DataFrame()
    #should retrieve for all projects, not only percolator
    for projectName in df_projects.project.unique():
        logging.info(instance,projectName)
        data_tmp = retrieveNFromeES(index_name, host, projectName, 3, startDate, debug=False)
        df_log_tmp = pd.DataFrame(data_tmp, columns=['index', 'type', 'id', 'routing', 'body'])
        df_Nlogs = df_Nlogs.append(df_log_tmp, ignore_index=True)
        #for test
        #print("{} project query done, records {}".format(projectName, len(data_tmp)))
        #if df_Nlogs.shape[0] >= 1:
        #    break
    df_Nlogs.to_csv("./{}-{}-Nlogs.csv".format(index_name, instance), sep=",", encoding="utf-8", index=False)
