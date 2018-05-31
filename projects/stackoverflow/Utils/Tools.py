import socket
import dill
import pickle
import sys

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def flushPrint(msg):
    print(msg)
    sys.stdout.flush()


def pickleDump(filename, obj):
    # store the content
    with open(filename, 'wb') as handle:
        pickle.dump(obj, handle)


def pickleLoad(filename):
    # load the content
    with open(filename, "rb") as handle:
        return pickle.load(handle)


def dillDump(filename, obj):
    with open(filename, 'wb') as handle:
        dill.dump(obj, handle)


def dillLoad(filename):
    # load the content
    with open(filename, "rb") as handle:
        return dill.load(handle)
