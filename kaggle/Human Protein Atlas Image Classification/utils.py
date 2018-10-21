"""
functions in the file are all common utils that other module need
"""
import pandas as pd
import numpy as pd
import os
import shutil

def readCategories(fileName="./categories.txt"):
    """
    # Description: read all category indexes and names from disk file.
    # Arguments
        fileName: the file which categories are saved in
    # Returns
        dict of categories: {index:{'name':value}}
    # Raises
        None
    """
    categories = {}
    dfCategories = pd.read_csv(fileName)
    print(dfCategories.shape)
    categories = dfCategories.set_index('index').T.to_dict("dict")
    return categories


def readLabels(fileName="./train.csv"):
    """
    # Description: read labels for the samples.
    # Arguments
        fileName: the file which label are saved in
    # Returns
        list of sample id and label list: [{'id':, 'targetList':[]}]
    # Raises
        None
    """
    labels = {}
    dfLabels = pd.read_csv(fileName)
    dfLabels['targetList'] = dfLabels.Target.str.split(' ')
    dfLabels.drop('Target',axis=1, inplace=True)
    print(dfLabels.head())
    labels = dfLabels.to_dict("recods")
    return labels


def rebuildDir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)