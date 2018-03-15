# coding: utf-8

# In[ ]:
import socket
import pickle

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def pickleDump(filename, obj):
    #store the content
    with open(filename, 'wb') as handle:
        pickle.dump(obj, handle)
        
def pickleLoad(filename):
    #load the content
    return pickle.load(open(filename, "rb" ) )