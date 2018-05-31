import xml.etree.ElementTree as ET
import re
import pandas as pd

FIELDNAME_ID = "docID"
FIELDNAME_POSTTYPE = "posttypeid"
FIELDNAME_ACCEPTEDANSWER = "acceptedanswerid"
FIELDNAME_CRTDATE = "creationdate"
FIELDNAME_BODY = "body"
FIELDNAME_TITLE = "title"
FIELDNAME_TAGS = "tags"
FIELDNAME_ANSWERCOUNT = "answercount"
KEEP_FIELDS = [FIELDNAME_ID,
               FIELDNAME_CRTDATE,
               FIELDNAME_BODY,
               FIELDNAME_TITLE,
               FIELDNAME_TAGS]

EXCLUDE_TAGS = ["git","svn",
           "sql", "regex","exception", "css", "html", "python", "c#", "asp.net",
           "ide", "visual-studio", "android-studio", "intellij", "xcode", "pycharm", "eclipse", "webstorm", "netbeans","delphi",
           "gcc", "g++", "cmake", "maven", "gradle",
           "excel", "word", "powerpoint", "outlook", "pdf", "notepad","notepad++", "vim", "vi", "emacs", "sublime"
           ]

def parseXMLAndFilterFunc(event, elem):
    try:
        values = dict()
        for key in elem.attrib.keys():
            if key.lower() == FIELDNAME_POSTTYPE \
                    or key.lower() == FIELDNAME_ACCEPTEDANSWER \
                    or key.lower() == FIELDNAME_CRTDATE\
                    or key.lower() == FIELDNAME_BODY \
                    or key.lower() == FIELDNAME_TITLE \
                    or key.lower() == FIELDNAME_TAGS \
                    or key.lower() == FIELDNAME_ANSWERCOUNT:
                values[key.lower()] = elem.attrib.get(key)
            elif key.lower() == "id":  # change field name to docID
                values[FIELDNAME_ID] = elem.attrib.get(key)
            else:
                # values[key.lower()] = elem.attrib.get(key)
                continue

        ### filter posts ###
        if FIELDNAME_POSTTYPE not in values or values[FIELDNAME_POSTTYPE] != "1":
            return None

        answercount = 0
        acceptedanswer = ""
        tags = []
        if FIELDNAME_ANSWERCOUNT in values and values[FIELDNAME_ANSWERCOUNT].isdecimal():
            answercount = int(values[FIELDNAME_ANSWERCOUNT])
        if FIELDNAME_ACCEPTEDANSWER in values:
            acceptedanswer = values[FIELDNAME_ACCEPTEDANSWER].strip()
        if FIELDNAME_TAGS in values:
            tags = [x for x in re.split("[<>]", values[FIELDNAME_TAGS].strip().lower()) if x]
            values[FIELDNAME_TAGS] = tags
            for exclude_tag in EXCLUDE_TAGS:
                if exclude_tag in tags:
                    return None

        if answercount == 0 or acceptedanswer == "":
            return None

        return [values[key] for key in KEEP_FIELDS]

    except Exception as e:
        print(e)
        return None

def loadStackoverflowFromXML(XMLFile, maxCount = -1):
    context = ET.iterparse(XMLFile, events=("start", "end"))
    #turn it into an iterator
    context = iter(context)
    #get the root element
    event, root = next(context)
    count = 0
    data = []
    for event, elem in context:
        if maxCount > 0 and count > maxCount:
            break
        if event == "end" and elem.tag == "row":
            values = parseXMLAndFilterFunc(event, elem)
            elem.clear()
            if values is not None:
                data.append(values)
                count += 1
        root.clear()
    print("Parse XML [%s]Done, total [%d] records!" % (XMLFile, count))
    return pd.DataFrame(data, columns=KEEP_FIELDS)

def getStackoverflowTags(XMLFile):
    context = ET.iterparse(XMLFile, events=("start", "end"))
    #turn it into an iterator
    context = iter(context)
    #get the root element
    event, root = next(context)
    data = []
    for event, elem in context:
        if event == "end" and elem.tag == "row":
            try:
                for key in elem.attrib.keys():
                    if key.lower() == FIELDNAME_TAGS:
                        tags = [x for x in re.split("[<>]", elem.attrib.get(key).strip().lower()) if x]
                        data.extend(tags)
            except Exception as e:
                print(e)
        root.clear()
    print("Parse XML [%s]Done, total [%d] tags!" % (XMLFile, len(data)))
    return data

#######test######
#df = loadStackoverflowFromXML(r"F:\stackoverflow.com-Posts\Posts.xml", 200)
#df["creationdate"] = pd.to_datetime(df["creationdate"])
#print(df.head)
#print(type(df.creationdate))
#print(df.creationdate.dt.year == 2008)
#print(df[df.creationdate.dt.year != 2008])
