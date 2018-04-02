## following are all processing functions for stackoverflow data
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords 
import spacy
import re
import string
import math
import multiprocessing
import time
from bs4 import BeautifulSoup

from Utils import utilTools
import importlib
importlib.reload(utilTools)

FIELDNAME_BODY = "body"
FIELDNAME_POSTTYPE = "posttypeid"
FIELDNAME_ANSWERCOUNT = "answercount"
FIELDNAME_ACCEPTEDANSWER = "acceptedanswerid"
FIELDNAME_ID = "docID"

"""
IDFILE="./1.pkl"
DATAFILE_CLEANED="./2.pkl"
DATAFILE_TOKENIZED="./3.pkl"
DATAFILE_VECTORIZED="./4.pkl"
VECTORIZERFILE = "./5.pkl"
"""

IDFILE="F:\stackoverflow.com-Posts\pkl\idlist_cleaned.pkl"
DATAFILE_CLEANED="F:\stackoverflow.com-Posts\pkl\preprocessed_data_cleaned.pkl"
DATAFILE_TOKENIZED="F:\stackoverflow.com-Posts\pkl\preprocessed_data_tokenized.pkl"
DATAFILE_VECTORIZED="F:\stackoverflow.com-Posts\pkl\preprocessed_data_vectorized.pkl"
VECTORIZERFILE = "F:\stackoverflow.com-Posts\pkl\\vectorizer.pkl"


punctuations = " ".join(string.punctuation).split(" ") + ["-----", "---", "...", "“", "”", "'ve", "--", "//", "div"]
parser = spacy.load('en', disable=['parser', 'ner'])

def parseXMLAndFilterFunc(event, elem):
    try:
        values=dict()
        for key in elem.attrib.keys():
            if key.lower() == FIELDNAME_BODY \
                or key.lower() == FIELDNAME_POSTTYPE \
                or key.lower() == FIELDNAME_ANSWERCOUNT \
                or key.lower() == FIELDNAME_ACCEPTEDANSWER:
                values[key.lower()] = elem.attrib.get(key)
            elif key.lower() == "id": # change field name to docID
                values[FIELDNAME_ID] = elem.attrib.get(key)
            else:
                #values[key.lower()] = elem.attrib.get(key)
                continue
            
        ### filter posts ###
        if FIELDNAME_POSTTYPE not in values or values[FIELDNAME_POSTTYPE] != "1":
            return None
            
        answercount = 0
        acceptedanswer = ""
        if FIELDNAME_ANSWERCOUNT in values and values[FIELDNAME_ANSWERCOUNT].isdecimal():
            answercount = int(values[FIELDNAME_ANSWERCOUNT])
        if FIELDNAME_ACCEPTEDANSWER in values:
            acceptedanswer = values[FIELDNAME_ACCEPTEDANSWER].strip()
                
        if answercount == 0 or acceptedanswer == "":
            return None
            
        return [values[FIELDNAME_ID], values[FIELDNAME_BODY]]
    except Exception as e:
        print(e)
        return None
    
def cleanTextFunc(text):
    #some data will raise NotImplementedError: subclasses of ParserBase must override error()
    try:
        bs = BeautifulSoup(text, "html.parser")
        #code = [s.extract() for s in bs('code')]
        # replace other HTML symbols
        text = bs.get_text()
    except Exception as e:
        #print(e)
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

#only keep nouns and adjectives
def tokenFunc(sentence):
    try:
        tokens = parser(sentence)
        #only keep nouns
        tokens = [tok for tok in tokens if (tok.tag_ in ("NN", "NNS", "NNP", "NNPS", "JJ"))]
        tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
        tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuations)]
        #remove tokens lenth is 1
        tokens = [tok for tok in tokens if (len(tok)>1)]
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
        print(e)
        print(sentence)
        tokens=[]
    return tokens

def tokenInChunks(data_in, n_jobs=1, n_chunks=1):
    #split data_in into n_chunks parts 
    # for multiprocessing 'i' format requires -2147483648 <= number <= 2147483647
    chunk_size = int(math.ceil(len(data_in) / n_chunks))
    tokenized_data = []
    start_time = time.time()
    if n_jobs>1:
        pool = multiprocessing.Pool(n_jobs)
        for i in range(n_chunks):
            tokenized_data_tmp = pool.map(tokenFunc, data_in[chunk_size*i:chunk_size*(i+1)])
            end_time = time.time()
            print("tokenized {} records in {} seconds".format(chunk_size*(i+1), end_time - start_time))
            tokenized_data.extend(tokenized_data_tmp) 
        try:
            utilTools.pickleDump(DATAFILE_TOKENIZED+str(i), tokenized_data_tmp)
        except Exception as e:
            print(e)
            print("pickleDump tokenized data Failed")
        pool.close()
        pool.join()
    else:
        for i in range(n_chunks):
            tokenized_data_tmp = [tokenFunc(x) for x in data_in[chunk_size*i:chunk_size*(i+1)]]
            end_time = time.time()
            print("tokenized {} records in {} seconds".format(chunk_size*(i+1), end_time - start_time))
            tokenized_data.extend(tokenized_data_tmp) 
        try:
            utilTools.pickleDump(DATAFILE_TOKENIZED+str(i), tokenized_data_tmp)
        except Exception as e:
            print(e)
            print("pickleDump tokenized data Failed")
    return tokenized_data
    
def saveCleanedData(idlist, data):
    try:
        utilTools.pickleDump(IDFILE, idlist)
        utilTools.pickleDump(DATAFILE_CLEANED, data)
    except Exception as e:
        print(e)
        print("save failed, idfile={}, dataFile={}".format(IDFILE, DATAFILE_CLEANED))
        raise e
        
# EOFError: Ran out of input, if file size is 0
def loadCleanedData():
    try:
        idlist = utilTools.pickleLoad(IDFILE)
        data = utilTools.pickleLoad(DATAFILE_CLEANED)
    except Exception as e:
        print(e)
        print("load failed, idfile={}, dataFile={}".format(IDFILE, DATAFILE_CLEANED))
        raise e
        
    return idlist, data  

def loadChunkedTokenizedData(n_chunks=1):
    try:
        data=[]
        for i in range(n_chunks):
            data_tmp = utilTools.pickleLoad(DATAFILE_TOKENIZED+str(i))
            data.extend(data_tmp)
        return data
    except Exception as e:
        print(e)
        print("loadChunkedTokenizedData failed")
        return None
    
def saveVectorizedData(data, vectorizer):
    try:
        utilTools.pickleDump(DATAFILE_VECTORIZED, data)
        utilTools.dillDump(VECTORIZERFILE, vectorizer)
    except Exception as e:
        print(e)
        print("save failed,dataFile={}, vectorizerFile={}".format(DATAFILE_VECTORIZED, VECTORIZERFILE))
        raise e
        
def loadVectorizedData():
    try:
        data = utilTools.pickleLoad(DATAFILE_VECTORIZED)
        vectorizer = utilTools.dillLoad(VECTORIZERFILE)
    except Exception as e:
        print(e)
        print("load failed, dataFile={}, vectorizerFile={}".format(DATAFILE_VECTORIZED, VECTORIZERFILE))
        raise e
        
    return data, vectorizer