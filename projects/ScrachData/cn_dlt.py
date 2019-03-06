# http://www.cnblogs.com/260554904html/p/9043581.html

import requests
import pandas as pd
from bs4 import BeautifulSoup

url = 'http://kaijiang.cpzj.com/dlt/kjlist.html?spanType=0&span=20000'
total_page = 151
cols = ['serial_no',
        'open_date',
        'b1', 'b2', 'b3', 'b4', 'b5',
        'r1', 'r2']

data = []
# 定义区列表

print("downloading page: " + url)

try:
    res = requests.get(url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find('table', {"class": "his-table"})
    content = table.find_all('tr')
except Exception as e:
    print(e)
    #print(content)
    #print (type(content))


for element in content:
    datum = {}
    try:
        cells = element.find_all('td')
        if len(cells) != 11:
            continue
        # only need the first 4 tds
        datum[cols[0]] = cells[0].text
        datum[cols[1]] = cells[1].text
        datum[cols[2]] = cells[2].select('span.hongQs')[0].text
        datum[cols[3]] = cells[2].select('span.hongQs')[1].text
        datum[cols[4]] = cells[2].select('span.hongQs')[2].text
        datum[cols[5]] = cells[2].select('span.hongQs')[3].text
        datum[cols[6]] = cells[2].select('span.hongQs')[4].text
        lanQs = cells[3].select('span.lanQs')[0].text.split()
        datum[cols[7]] = lanQs[0]
        datum[cols[8]] = lanQs[1]
        data.append(datum)
        #print("one row test:", datum)
        #break
    except Exception as e:
        #print(e)
        pass

df = pd.DataFrame(data)
#print(data)
print(df.head())
df.to_csv('./data_out/cn_dlt.csv', index=False, columns=cols)
