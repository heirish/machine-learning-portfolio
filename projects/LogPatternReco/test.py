##test1
import math
from random import shuffle

from Modules import AlignNW, HC

aligner = AlignNW.AlignNW(1, -1, -2)
texts = ["""query2.lycos.cs.cmu.edu [29:23:53:36] "GET /Consumer.html HTTP/1.0" 200 1325\n""",
         """wpbfl2-45.gate.net [29:23:54:16] "GET /icons/circle_logo_small.gif HTTP/1.0" 200 2624\n""",
         """wpbfl2-45.gate.net [29:23:54:18] "GET /logos/small_gopher.gif HTTP/1.0" 200 935\n""",
         """wpbfl2-45.gate.net [29:23:54:19] "GET /logos/small_ftp.gif HTTP/1.0" 200 124"""
         ]
texts = ["""141.243.1.172 [29:23:53:25] "GET /Software.html HTTP/1.0" 200 1497""",
         """query2.lycos.cs.cmu.edu [29:23:53:36] "GET /Consumer.html HTTP/1.0" 200 1325""",
         """tanuki.twics.com [29:23:53:53] "GET /News.html HTTP/1.0" 200 1014""",
         """wpbfl2-45.gate.net [29:23:54:15] "GET / HTTP/1.0" 200 4889""",
         """wpbfl2-45.gate.net [29:23:54:16] "GET /icons/circle_logo_small.gif HTTP/1.0" 200 2624""",
         """wpbfl2-45.gate.net [29:23:54:18] "GET /logos/small_gopher.gif HTTP/1.0" 200 935""",
         """140.112.68.165 [29:23:54:19] "GET /logos/us-flag.gif HTTP/1.0" 200 2788""",
         """wpbfl2-45.gate.net [29:23:54:19] "GET /logos/small_ftp.gif HTTP/1.0" 200 124""",
         """wpbfl2-45.gate.net [29:23:54:19] "GET /icons/book.gif HTTP/1.0" 200 156""",
         """wpbfl2-45.gate.net [29:23:54:19] "GET /logos/us-flag.gif HTTP/1.0" 200 2788""",
         """tanuki.twics.com [29:23:54:19] "GET /docs/OSWRCRA/general/hotline HTTP/1.0" 302 -""",
         """wpbfl2-45.gate.net [29:23:54:20] "GET /icons/ok2-0.gif HTTP/1.0" 200 231""",
         """tanuki.twics.com [29:23:54:25] "GET /OSWRCRA/general/hotline/ HTTP/1.0" 200 991""",
         """tanuki.twics.com [29:23:54:37] "GET /docs/OSWRCRA/general/hotline/95report HTTP/1.0" 302 -""",
         """wpbfl2-45.gate.net [29:23:54:37] "GET /docs/browner/adminbio.html HTTP/1.0" 200 4217""",
         """tanuki.twics.com [29:23:54:40] "GET /OSWRCRA/general/hotline/95report/ HTTP/1.0" 200 1250""",
         """wpbfl2-45.gate.net [29:23:55:01] "GET /docs/browner/cbpress.gif HTTP/1.0" 200 51661""",
         """dd15-032.compuserve.com [29:23:55:21] "GET /Access/chapter1/s2-4.html HTTP/1.0" 200 4602""",
         """tanuki.twics.com [29:23:55:23] "GET /docs/OSWRCRA/general/hotline/95report/05_95mhr.txt.html HTTP/1.0" 200 56431""",
         """wpbfl2-45.gate.net [29:23:55:29] "GET /docs/Access HTTP/1.0" 302 -""",
         """140.112.68.165 [29:23:55:33] "GET /logos/us-flag.gif HTTP/1.0" 200 2788""",
         """wpbfl2-45.gate.net [29:23:55:46] "GET /information.html HTTP/1.0" 200 617""",
         """wpbfl2-45.gate.net [29:23:55:47] "GET /icons/people.gif HTTP/1.0" 200 224""",
         """wpbfl2-45.gate.net [29:23:56:03] "GET /docs/Access HTTP/1.0" 302 -""",
         """wpbfl2-45.gate.net [29:23:56:12] "GET /Access/ HTTP/1.0" 200 2376""",
         """wpbfl2-45.gate.net [29:23:56:14] "GET /Access/images/epaseal.gif HTTP/1.0" 200 2624"""
        ]
#alignedText = ""
#for text in texts:
#    time.sleep(5)
#    if not alignedText :
#        alignedText = text
#        continue
#    textList1 = HC.tokenize(HC.preprocess(alignedText))
#    textList2 = HC.tokenize(HC.preprocess(text))
#    #print(textList1)
#    #print(textList2)
#    alignedList1, alignedList2, alignedList = aligner.doAlign(textList1, textList2)
#    print(alignedList1)
#    print(alignedList2)
#    print(alignedList)
#    alignedText = "".join(HC.remove_excessive_duplicates(alignedList, '*', 5))
#    print(alignedText)

n_chunks = 4
shuffle(texts)
chunk_size = int(math.ceil(len(texts)/n_chunks))
alignedTexts = []
for i in range(n_chunks):
    texts_tmp = texts[i*chunk_size:(i+1)*chunk_size]
    alignedText = ""
    for text in texts_tmp:
        if not alignedText :
            alignedText = text
            continue
        textList1 = HC.tokenize(HC.preprocess(alignedText))
        textList2 = HC.tokenize(HC.preprocess(text))
        _, _, alignedList = aligner.doAlign(textList1, textList2)
        alignedText = "".join(HC.remove_excessive_duplicates(alignedList, '*', 5))
    alignedTexts.append(alignedText)

alignedText = ""
for text in alignedTexts:
    print(text)
    if not alignedText:
        alignedText = text
        continue
    textList1 = HC.tokenize(HC.preprocess(alignedText))
    textList2 = HC.tokenize(HC.preprocess(text))
    _, _, alignedList = aligner.doAlign(textList1, textList2)
    alignedText = "".join(HC.remove_excessive_duplicates(alignedList, '*', 5))
print(alignedText)

#import string
#from zhon import hanzi
#delimiter = string.punctuation.replace('_', "").replace("-", "").replace("*", "") + "\\\\"
## add hanzi punctuations
#delimiter += hanzi.punctuation
## add space
#delimiter += ' '
#print(delimiter)
