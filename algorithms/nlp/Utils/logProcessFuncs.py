from bs4 import BeautifulSoup
import string
import spacy
import re
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords 
from zhon import hanzi #for CJK punctuations

from Utils import utilIdentifier
import importlib
importlib.reload(utilIdentifier)

punctuations = " ".join(string.punctuation).split(" ") + " ".join(hanzi.punctuation).split(" ")
parser = spacy.load('en', disable=['parser', 'ner'])

def cleanTextFunc(text):
    #some data will raise NotImplementedError: subclasses of ParserBase must override error()
    try:
        bs = BeautifulSoup(text, "html.parser")
        text_p = bs.get_text()
        text = text_p
    except Exception as e:
        pass
    
    try:
        # get rid of newlines
        text = text.strip().replace("\n", " ").replace("\r", " ")
        # delete unicode, or multiprocessing.map will raise encodeerror
        text = text.encode("utf-8", "ignore").decode()
    
        #identify predefined-types
        text = utilIdentifier.identifyIP(text)
        text = utilIdentifier.identifyDatetime(text)
        text = utilIdentifier.identifyUri(text)
        text = utilIdentifier.identifySQLSelect(text)
    except Exception as e:
        print(e)
        print("text:{0}".format(text))
        pass
    
    return text

def splitTextFunc(text):
    try:
        #text = re.sub("([{}])".format(string.punctuation), r' \1 ', text)
        #english words might contain -_
        #|||| is quote to | in sub
        delimiter = string.punctuation.replace('_', "").replace("-", "") + "\\\\"
        #add hanzi punctuations
        delimiter += hanzi.punctuation
        text = re.sub("([{}])".format(delimiter), r' \1 ', text)
    except Exception as e:
        pass
    return text


def tokenFunc(sentence):
    try:
        tokens = parser(sentence)
        tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
        tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuations)]
        #only keep tokens length in [2,32]
        tokens = [tok for tok in tokens if (len(tok)>1 and len(tok) < 33)]
        #remove tokens start or end with "-", command line parameter
        tokens = [tok for tok in tokens if (not tok.startswith("-") and not tok.endswith("-"))]
        #remove numeric
        tokens = [tok for tok in tokens if (tok.isnumeric() is not True)]
        #remove words contains both alphabet and number, those might be the encoded id or keys.
        tokens = [tok for tok in tokens if not (re.search('\d', tok) and re.search("[a-z]", tok, re.IGNORECASE))]
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
