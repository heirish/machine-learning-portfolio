# coding: utf-8

# In[ ]:
import datefinder
import importlib
importlib.reload(datefinder)
import re
import ipaddress
from urllib.parse import urlparse
import spacy

########################NOTE:typeName should all not begin or end with number, for datefinder bug##############################

#https://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses/1934546
#http://nbviewer.jupyter.org/github/rasbt/python_reference/blob/master/tutorials/useful_regex.ipynb
"""
IPV4SEG  = (25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])
IPV4ADDR = (IPV4SEG\.){3,3}IPV4SEG
IPV6SEG  = [0-9a-fA-F]{1,4}
IPV6ADDR = (
           (IPV6SEG:){7,7}IPV6SEG|                # 1:2:3:4:5:6:7:8
           (IPV6SEG:){1,7}:|                      # 1::                                 1:2:3:4:5:6:7::
           (IPV6SEG:){1,6}:IPV6SEG|               # 1::8               1:2:3:4:5:6::8   1:2:3:4:5:6::8
           (IPV6SEG:){1,5}(:IPV6SEG){1,2}|        # 1::7:8             1:2:3:4:5::7:8   1:2:3:4:5::8
           (IPV6SEG:){1,4}(:IPV6SEG){1,3}|        # 1::6:7:8           1:2:3:4::6:7:8   1:2:3:4::8
           (IPV6SEG:){1,3}(:IPV6SEG){1,4}|        # 1::5:6:7:8         1:2:3::5:6:7:8   1:2:3::8
           (IPV6SEG:){1,2}(:IPV6SEG){1,5}|        # 1::4:5:6:7:8       1:2::4:5:6:7:8   1:2::8
           IPV6SEG:((:IPV6SEG){1,6})|             # 1::3:4:5:6:7:8     1::3:4:5:6:7:8   1::8
           :((:IPV6SEG){1,7}|:)|                  # ::2:3:4:5:6:7:8    ::2:3:4:5:6:7:8  ::8       ::       
           fe80:(:IPV6SEG){0,4}%[0-9a-zA-Z]{1,}|  # fe80::7:8%eth0     fe80::7:8%1  (link-local IPv6 addresses with zone index)
           ::(ffff(:0{1,4}){0,1}:){0,1}IPV4ADDR|  # ::255.255.255.255  ::ffff:255.255.255.255  ::ffff:0:255.255.255.255 (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
           (IPV6SEG:){1,4}:IPV4ADDR               # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
           )
"""


IPV4SEG  = "(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])"
IPV4ADDR = "({ipv4_seg}\.){{3,3}}{ipv4_seg}".format(ipv4_seg=IPV4SEG)
IPV6SEG  = "[0-9a-fA-F]{1,4}"
IPV6ADDR = """(
           ({ipv6_seg}:){{7,7}}{ipv6_seg}|            
           {ipv6_seg}:((:{ipv6_seg}){{1,6}})|
           [fF][eE]80:(:{ipv6_seg}){{0,4}}%[0-9a-zA-Z]{{1,}}|
           [fF][eE]80:(:{ipv6_seg}){{0,4}}|
           ::(ffff(:0{{1,4}}){{0,1}}:){{0,1}}{ipv4_addr}|
           ({ipv6_seg}:){{1,4}}:{ipv4_addr}
           )""".format(ipv6_seg=IPV6SEG,ipv4_addr=IPV4ADDR)
IPV4_REGEX=re.compile(IPV4ADDR, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)
IPV6_REGEX=re.compile(IPV6ADDR, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

URI="((https?|ftp|gopher|telnet|file):((//)|(\\\\))+[\\w\\d:#@%/;$()~_?\\+-=\\\\\\.&]*)"
URI_REGEX=re.compile(URI, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

parser = spacy.load('en', disable=['parser', 'ner'])

def formatTypeName(typeName):
    return "{}".format(typeName)

#########Caution:this will identify man numbers to wrong datetime
###seems set strict to True when call extract_date_string can resolve that prob
def identifyDatetime(text, typeName="DATETIME_TYPE"):
    finder = datefinder.DateFinder()
    #print(finder.DATES_PATTERN)
    finds = finder.extract_date_strings(text, strict=True)
    for date_string, indices, captures in finds:
        #print(date_string)
        #print(indices)
        #print(captures)
        parsed_date = finder.parse_date_string(date_string, captures)
        if parsed_date is not None:
            #print(parsed_date)
            text = text.replace(date_string, formatTypeName(typeName))
    return text

#not work well for logs, log differ from normal NLP
def identifyDTWithSpacy(text, typeName="DATETIME_TYPE"):
    doc = parser(text)
    for ent in doc.ents:
        if ent.label_ == "DATE" or ent.label_ == "TIME":
            text = text.replace(ent, formatTypeName(typeName))
    return text

def identifyIPv4(text, typeName="IPV4_TYPE"):
    for match in IPV4_REGEX.finditer(text):
        try:
            matched_ip = match.group()
            ipaddress.ip_address(matched_ip)
            text = text.replace(matched_ip, formatTypeName(typeName))
        except Exception as e:
            pass
    #handle ip like fe80::20c:29ff:fe75:f519/64
    text=re.sub(typeName+"\/\d+", typeName, text)
    return text

def identifyIPv6(text, typeName="IPV6_TYPE"):
    #print(IPV6ADDR)
    for match in IPV6_REGEX.finditer(text):
        try:
            matched_ip = match.group()
            #print(matched_ip)
            ipaddress.ip_address(matched_ip)
            text = text.replace(matched_ip, formatTypeName(typeName))
        except Exception as e:
            pass
        
    #handle ip like fe80::20c:29ff:fe75:f519/64
    text=re.sub(typeName+"\/\d+", typeName, text)
    return text

def identifyIP(text, typeNameV4="IP_TYPE", typeNameV6="IP_TYPE"):
    text = identifyIPv4(text, typeNameV4)
    text = identifyIPv6(text, typeNameV6)
    return text

def identifyUri(text,typeName="URL_TYPE"):
    for match in URI_REGEX.finditer(text):
        try:
            matched_uri = match.group()
            urlparse(matched_uri)
            text = text.replace(matched_uri, formatTypeName(typeName))
        except Exception as e:
            pass
    
    return text

#these comman types should be identified last
def identifyNumber(text, typeName="NUM_TYPE"):
    replaced_text = ""
    last_index = 0
    for match in re.finditer("[/\:\-\,\s\_\+\@=]\d+[\s\,\.]",text):
        matched_number = match.group()[1:].rstrip(" ,.")
        if matched_number.isnumeric():
            replaced_text += text[last_index:match.start()+1] + formatTypeName(typeName)
            last_index = match.end()-1
    if last_index > 0:
        replaced_text += text[last_index:]
        
    if len(replaced_text) > 0:
        return replaced_text
    
    return text

def identifySQLSelect(text, typeName="SQLSELECT_TYPE"):
    replaced_text = ""
    last_index = 0
    for match in re.finditer(r"(?i)select\s.*from\s.*(where)?.*(and|or)?.*[,|.|;|]", text):
        matched_sql = match.group()
        replaced_text += text[last_index:match.start()] + formatTypeName(typeName)
        last_index = match.end()-1
    
    if last_index > 0:
        replaced_text += text[last_index:]
        
    if len(replaced_text) > 0:
        return replaced_text
    
    return text
    
def isJavaStackTrace(text):
    #if re.search(r"Caused by:.*", text) \
        #and 
    if re.search(r"(?i)(at)?.*\(.*.java:\d+\)", text):
        return True
    else:
        return False

def isJSStackTrace(text):
    #if re.search(r"Caused by:.*", text) \
        #and 
    if re.search(r"(?i)(at)?.*\(.*.js:\d+\)", text):
        return True
    else:
        return False
