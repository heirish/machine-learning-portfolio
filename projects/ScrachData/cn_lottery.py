# http://www.cnblogs.com/260554904html/p/9043581.html

import requests
import pandas as pd
from bs4 import BeautifulSoup

url = 'http://kaijiang.zhcw.com/zhcw/html/ssq/list_{page}.html'
total_page = 151
cols = ['open_date', 'serial_no',
        'bonus_no0', 'bonus_no1',
        'bonus_no2', 'bonus_no3',
        'bonus_no4', 'bonus_no5',
        'bonus_no6']

data = []
# 定义区列表
for j in range(0, total_page+1):
    if j == 0:
        lottery_url = 'http://kaijiang.zhcw.com/zhcw/html/ssq/list.html'
    else:
        lottery_url = url.format(page=j)

    print("downloading page: " + lottery_url)
    try:
        res = requests.get(lottery_url, verify=False)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table', {"class": "wqhgt"})
        content = table.find_all('tr')
    except Exception as e:
        print(e)
        continue
        # print(content)
        # print (type(content))

    for element in content:
        datum = {}
        try:
            cells = element.find_all('td')
            if len(cells) != 7:
                continue
            # only need the first 3 tds
            datum[cols[0]] = cells[0].text
            datum[cols[1]] = cells[1].text
            datum[cols[2]] = cells[2].select('em')[0].text
            datum[cols[3]] = cells[2].select('em')[1].text
            datum[cols[4]] = cells[2].select('em')[2].text
            datum[cols[5]] = cells[2].select('em')[3].text
            datum[cols[6]] = cells[2].select('em')[4].text
            datum[cols[7]] = cells[2].select('em')[5].text
            datum[cols[8]] = cells[2].select('em')[6].text
            data.append(datum)
        except Exception as e:
            pass

df = pd.DataFrame(data)
print(data)
df.head()
df.to_csv('./data_out/lottery.csv', index=False, columns=cols)
