# coding: utf-8

# In[ ]:
import socket
import dill #for pickle  object with lambdas
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
    with open(filename, "rb") as handle:
        return pickle.load(handle)
    
def dillDump(filename, obj):
    with open(filename, 'wb') as handle:
        dill.dump(obj, handle)
        
def dillLoad(filename):
    #load the content
    with open(filename, "rb") as handle:
        return dill.load(handle)
    
def formatOneTextRow(fields, values = None, fieldDLM="|@|"):
    """
    Parameters in:
        fields - a list of fields name
        values - a dictionary of values with fields name, Default None
        fieldDLM - delimeter of values, default "|@|"
    Return:
        if values is None, return fields with delimeters, used as header
        if is not None, values with delimeters in the same order as fields
    """
    #format a header
    if values is None:
        return fieldDLM.join(fields)
    
    #format a data row
    valueList = []
    for field in fields:
        if field in values:
            if field == "tags":
                valueList.append(",".join(values[field]))
            else:
                valueList.append(values[field])
        else: 
            valueList.append("")
    return fieldDLM.join(valueList)