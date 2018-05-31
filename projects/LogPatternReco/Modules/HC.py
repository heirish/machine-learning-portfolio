## this is a stream input data example. the data is not processed in batch, it's processed one by one.
### 1. identify datetime, IP
### 2. tokenization: split text and identify number
### 3. cluster
### 4. alignment
### 5. pattern retrieve

import importlib
import re
import string

import spacy
from treelib import Tree
from zhon import hanzi  # for CJK punctuations

from Modules import AlignNW, DataSource
from Utils import Identifier

importlib.reload(Identifier)
importlib.reload(AlignNW)
importlib.reload(DataSource)

punctuations = " ".join(string.punctuation).split(" ") + " ".join(hanzi.punctuation).split(" ")
parser = spacy.load('en', disable=['parser', 'ner'])
aligner = AlignNW.AlignNW(1, -1, -2)

def remove_excessive_duplicates(iterable, dup='', max_dup=2):
    """Generate items in iterable, but at most max_dup of any consecutive
    sequence of items equal to dup.

    >>> input = [1, 0, 0, 0, 2, 0, 3, 0, 0, 0, 0, 0, 4, 0]
    >>> list(remove_excessive_duplicates(input, dup=0))
    [1, 0, 0, 2, 0, 3, 0, 0, 4, 0]

    """
    count = 0
    lastitem = None
    #最后一个空格，不要替换掉
    for item in iterable:
        if item == dup or item == ' ':
            count += 1
        else:
            count = 0
            #if lastitem == ' ':
            #    yield lastitem
        #lastitem = item
        if count <= max_dup:
            yield item

    #for key, group in groupby(iterable):
    #    yield from islice(group, max_dup) if key == dup else group

### identify datetime, IP
#because these pre-defined types are not so valuable to the pattern recognition. we will ignore these info.
def preprocess(text):
    try:
        # delete unicode, or multiprocessing.map will raise encodeerror
        text = text.encode("utf-8", "ignore").decode()

        # identify predefined-types
        text = Identifier.identifyIP(text)
        text = Identifier.identifyDatetime(text)
    except Exception as e:
        print(e)
        print("text:{0}".format(text))
        pass

    return text

### tokenization: split text and identify number
def tokenize(text):
    # split text
    try:
        # english words might contain -_
        # |||| is quote to | in sub
        # keep * in pattern
        delimiter = string.punctuation.replace('_', "").replace("-", "").replace("*", "") + "\\\\"
        # add hanzi punctuations
        delimiter += hanzi.punctuation
        # add space
        text = re.sub("([{}])".format(delimiter + ' '), r' \1 ', text)
    except Exception as e:
        pass

    # tokenize and identify number
    try:
        tokens = parser(text)
        tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
        # keep blank space in tokens
        tokens = [' ' if not tok else tok for tok in tokens]
        #match [del][space][space][del], and remove the two spaces
        cleaned_tokens = []
        i = 0
        #becuase parse already delete a blank space
        while i < len(tokens)-3:
            cleaned_tokens.append(tokens[i])
            if tokens[i] in delimiter and tokens[i+2] in delimiter:
                if tokens[i+1] == ' ':
                    i += 2
                    continue
            i += 1
        cleaned_tokens.extend(tokens[-3:])
        #tokens = remove_excessive_duplicates(tokens, ' ', max_dup=1)
        # identify numeric
        tokens = ["number_type" if tok.isnumeric() else tok for tok in cleaned_tokens]

    except Exception as e:
        print(e)
        print(text)
        tokens = []
    return tokens

def defaultDistFunc(text1, text2):
    #preprocess and token in FastCluster
    text1_tokens = text1
    text2_tokens = text2
    min_len = min(len(text1_tokens), len(text2_tokens))
    max_len = max(len(text1_tokens), len(text2_tokens))
    if max_len == 0:
        return 0
    score = 0
    for i in range(min_len):
        if text1_tokens[i] == text2_tokens[i]:
            score += 1
    dist = 1 - score / max_len
    #print("text: text1: {},\ntext2: {},\ndistance:{}"
    #      .format(text1, text2, dist))
    return dist

def earlystopDistFunc(text1, text2, maxDist):
    #preprocess and token in FastCluster
    text1_tokens = text1
    text2_tokens = text2
    min_len = min(len(text1_tokens), len(text2_tokens))
    max_len = max(len(text1_tokens), len(text2_tokens))
    if max_len == 0:
        return True
    minScore = (1-maxDist) * max_len
    score = 0
    for i in range(min_len):
        if text1_tokens[i] == text2_tokens[i]:
            score += 1
        if score > minScore:
            return True

    dist = 1 - score / max_len
    if dist <= maxDist:
        return True
    else:
        return False

def FastClustering(dataId, datasource, clusters, maxDist=0.5, distF=defaultDistFunc):
    if not clusters:
       return {0: {"pattern": "", "data": [], "unmerged": [dataId]}}
    if not isinstance(clusters, dict):
        print(type(clusters), clusters)
        raise ValueError("invalid clusters format")

    data_tokens = tokenize(preprocess(datasource.getTextFromId(dataId)))
    if data_tokens is None:
        raise ValueError("can not get text from id", dataId)
    node_ids = clusters.keys()
    found = False
    for node_id in node_ids:
        data_list = clusters[node_id]["data"]
        unmerged_data = clusters[node_id]["unmerged"]
        if not data_list and not unmerged_data:
            continue

        if data_list:
            node_representive = tokenize(preprocess(datasource.getTextFromId(data_list[0])))
            #delete data in unmerged_data that already merged
            unmerged_data = [id for id in unmerged_data if id not in data_list]
        else:
            node_representive = tokenize(preprocess(datasource.getTextFromId(unmerged_data[0])))

        #if distF(data_tokens, node_representive) <= maxDist:
        if earlystopDistFunc(data_tokens, node_representive, maxDist):
            unmerged_data.append(dataId)
            clusters[node_id]["unmerged"] =unmerged_data
            found = True
            break
    if not found:
        node_id = max(node_ids) + 1
        clusters[node_id] = {"pattern": "", "data": [], "unmerged": [dataId]}

    return clusters


### alignment:
#### from leaf to root, merge "pattern" with the last element in "data", update the "pattern" field
### 只更改data与pattern字段，不动unmerged字段
def doAlign(text1, text2):
    text1_tokens = tokenize(text1)
    text2_tokens = tokenize(text2)
    try:
        _, _, alignedList = aligner.doAlign(text1_tokens, text2_tokens)
        #the max
        alignedList = remove_excessive_duplicates(alignedList, '*', 5)
        alignedList = remove_excessive_duplicates(alignedList, ' ', 2)
        return "".join(alignedList)
    except Exception as e:
        print("Exception: {}. \nlist1: {} \nlist2:{}"
              .format(e, text1_tokens, text2_tokens))
    return None

def updatePatterns(datasource, clusters):
    for node_id, cluster in clusters.items():
        old_pattern = cluster["pattern"]
        data_list = cluster["data"]
        unmerged_data = cluster["unmerged"]
        if not unmerged_data:
            continue

        new_pattern = ""
        for dataId in unmerged_data:
            if dataId in data_list:
                continue
            if old_pattern == "":
                new_pattern = preprocess(datasource.getTextFromId(dataId)).lower()
            else:
                new_pattern = doAlign(preprocess(old_pattern),
                                      preprocess(datasource.getTextFromId(dataId)))
            if new_pattern:
                old_pattern = new_pattern
                data_list.append(dataId)

        if new_pattern:
            clusters[node_id]["pattern"] = new_pattern
            clusters[node_id]["data"] = data_list
            clusters[node_id]["unmerged"] = []
            ##index the "pattern", id, text
            #id = "C_{}_{}".format(level, node_id)
            #datasource.addItem(id, new_pattern):

    return clusters

def visualizeCtree(c_tree):
    #bottom up build tree
    tree = Tree()
    tree.create_node("root", "root")
    levels = sorted(c_tree.keys())
    for level in levels:
        for node_id, cluster in c_tree[level].items():
            node_id = "{}.{}".format(level, node_id)
            tree.create_node("{}".format(cluster["pattern"]), node_id, parent="root")
            if level == 0:
                for data in cluster["data"]:
                    tree.create_node("log.{}".format(data), "log.{}".format(data), parent=node_id)
            else:
                for data in cluster["data"]:
                    tree.move_node("{}.{}".format(level-1, data), node_id)
    tree.show()
    tree.save2file("./tree")


## How to use
##1. for log in logs:updateCTree, updatePatterns
##2. get the c_tree
##3. train all the logs to get the max level and estimate the best level we keep.
##4. train the cluster on different level
##要考虑到unmerged list的同步问题, 到时production考虑将c_tree存在redis里，然后同时flush到库里