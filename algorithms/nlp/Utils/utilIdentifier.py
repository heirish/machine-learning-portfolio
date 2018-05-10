# coding: utf-8

# In[ ]:
import datefinder
import importlib
importlib.reload(datefinder)
import re
import ipaddress
from urllib.parse import urlparse
import spacy
import base64
from zhon import hanzi #for CJK punctuations
import string

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

TERMINATERS = {'\n':'LINUX_NEWLINE',
          '\r\n':'WINDOWS_NEWLINE',
          '\s':'T_SPACE'}

#words may contain -_
#base64string include +=/
#IP may include ./:
#url may include /
split_delimiter = re.sub('[\-_=\+\./:]', '', string.punctuation)
split_delimiter += hanzi.punctuation
    
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

def isCommonEncoded(word):
    return re.search('\d', word) and re.search("[a-z]", word, re.IGNORECASE)

def isBase64(word):
    if not isinstance(word ,str) or not word:
        #raise ValueError("params s not string or None")
        return False
    if not isCommonEncoded(word):
        return False
    if word in parser.vocab:
        return False

    _base64_code = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
               'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
               'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a',
               'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
               'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
               't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1',
               '2', '3', '4','5', '6', '7', '8', '9', '+',
               '/', '=' ]

    # Check base64 OR codeCheck % 4
    code_fail = [ i for i in word if i not in _base64_code]
    if code_fail or len(word) % 4 != 0:
        return False
    
    try:
        return base64.b64encode(base64.b64decode(word)).decode() == word
    except Exception as e:
        #print(e)
        pass
    return False

def identifyBase64(text, typeName="BASE64_TYPE"):
    words = re.split("([{}])".format(split_delimiter), text)
    
    for i in range(len(words)):
        if isBase64(words[i]):
            words[i] = typeName
    
    return "".join(words)

def identifyXML(text, typeName = "XML_TYPE"):
    text = html.unescape(text)
    start_pos = text.find("<")
    end_pos = text.rfind(">")
    
    if start_pos == -1 or end_pos == -1 or end_pos < start_pos:
        return text
    while start_pos !=-1 and end_pos != -1 and end_pos > start_pos:
        xml_str = text[start_pos:end_pos+1]
        print("==========",start_pos, end_pos,"================",xml_str)
        try:
            root = ET.fromstring(xml_str)
            if root.tag is not None:
                text = text[:start_pos] + " {} ".format(typeName) + text[end_pos+1:]
        except Exception as e:
            print(e)
            pass
        start_pos = text.find("<", start_pos +1)
        end_pos = text.rfind(">", 0, end_pos)
        
    return text
#######################test#####################
text = """허용되지 않는 입력 입니다. &lt;?xml version=&apos;1.0&apos; encoding=&apos;UTF-8&apos;?&gt; &lt;message type=&apos;request&apos; version=&apos;1.0.0&apos; &gt; &lt;/message&gt;"""
#text = "this is not a html"
#text = "<p>Hello World!</p>"
#text = "<html><head><title>Title</title></head><body><p>Hello!</p></body></html>"
#text = "start<html><head><title>Title</title></head><body><p>Hello!</p></body></html>end"
#text = "start <html><head><title>Title</title></head><body><p>Hello!</p></body></html> end"
print(identifyXML(text))
###############################
    
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
