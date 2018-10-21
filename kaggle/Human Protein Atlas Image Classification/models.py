"""
the file contains all the models that we can try
"""

from keras.models import Sequential
from keras.layers import *
from keras import regularizers

def modelC7D3(imageShape, labelSize):
    model = Sequential()
    model.add(Conv2D(16, (3, 3), input_shape=imageShape, activation='relu', padding='same', name='block1_cov1'))
    # model.add(MaxPooling2D((2,2), padding='same', name='block1_pool1'))
    
    model.add(Conv2D(32, (3, 3), activation='relu', padding='same', name='block2_cov1'))
    model.add(MaxPooling2D((2,2), padding='same', name='block2_pool1'))
    
    # model.add(Conv2D(64, (3, 3), activation='relu', padding='same', name='block3_cov1'))
    # model.add(MaxPooling2D((2,2), padding='same', name='block3_pool1'))
 
    # model.add(Conv2D(128, (3, 3), activation='relu', padding='same', name='block4_cov1'))
    # model.add(Conv2D(128, (3, 3), activation='relu', padding='same', name='block4_cov2'))
    # model.add(MaxPooling2D((2,2), padding='same', name='block4_pool'))
    
    # model.add(Conv2D(256, (3, 3), activation='relu', padding='same', name='block5_cov1'))
    # model.add(Conv2D(256, (3, 3), activation='relu', padding='same', name='block5_cov2'))
    # model.add(Dropout(0.5))
    
    model.add(Flatten(name='flat'))
    # model.add(Dense(256, activation='relu', name='dense2'))
    # model.add(Dropout(0.5))
    # model.add(Dense(128, activation='relu', name='dense3'))
    model.add(Dense(32, activation='relu', name='dense3'))
    # model.add(Dense(1, activation='sigmoid', name='dense4'))
    model.add(Dense(labelSize, activation='softmax', name='dense4'))
        
    return model