"""
functions in the file are all common utils that other module need
"""
import pandas as pd
import numpy as np
import os
import shutil
import matplotlib.pyplot as plt
from keras.utils.vis_utils import plot_model, model_to_dot #newer
#from keras.utils.visualize_util import plot, model_to_dot
from IPython.display import Image, SVG

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
    
    
# visualize model
def visualizeModel(model, modelName=None):
    if model == None or modelName == None:
        raise Exception("in save_model, invalid parameter")    
    imageName = modelName + ".png"
    plot_model(model, to_file=imageName, show_shapes=True) #newer
    #plot(model, to_file=image_name, show_shapes=True)
    SVG(model_to_dot(model).create(prog='dot', format='svg'))
    
def visualizeHistory(history, modelName=None):
    if modelName == None:
        raise Exception("in visualize_history, please input your model_name")
    print(history.history.keys())
    plt.figure(figsize=(12,4))
    plt.subplot(1, 2,1)
    
    # summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title(modelName + ' model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'valid'], loc='center right')
    plt.subplots_adjust(wspace = .5)
    
    # summarize history for loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title(modelName + ' model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'valid'], loc='center right')
    
    plt.show()
    
#import h5py as h5py
try:
    import h5py
except ImportError:
    h5py = None
def saveModel(model, modelName):
    if model == None or modelName == None:
        raise Exception("in save_model, invalid parameter")
    #model.save_weights(modelName + '.h5')
    with open(modelName + '.json', 'w') as f:
        f.write(model.to_json())