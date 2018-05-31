#http://www.cnblogs.com/260554904html/p/9043581.html

import requests
import pandas as pd
from bs4 import BeautifulSoup
url='https://cd.lianjia.com/chengjiao/{areo}/pg{page}/'
data=[]
#定义区列表
sectionlist={'jinjiang':['chuanshi', 'dongkezhan', 'dongdalu', 'donghu', 'dongguangxiaoqu', 'hongxinglu', 'hejiangting',
                      'jiuyanqiao', 'jingjusi', 'lianhua2', 'liulichang', 'langudi', 'panchenggang', 'shahebao',
                      'shuilianhe', 'sanshengxiang', 'sanguantang', 'yanshikou', 'zhuojincheng'],
          'qingyang':['beisen', 'babaojie', 'caotang', 'caoshijie', 'funanxinqu', 'guanghuapaoxiao', 'huanhuaxi',
                      'jinsha', 'jiaolonggang', 'kuanzhaixiangzi', 'renmingongyuan', 'taishenglu', 'waiguanghua',
                      'waijinsha', 'wanjiawan', 'xinancaida', 'youpindao'],
          'wuhou':['chuanda', 'chuanyin','caojinlijiao','cuqiao','guangfuqiao','gaoshengqiao','huaxi','hangkonglu',
                   'huochenanzhan','hongpailou','hangkonggang','longwan','lidu','shuangnan','tongzilin','wuhoulijiao',
                   'wuhouci','waishuangnan','wudahuayuan','xinshuangnan','yulin','zongbei'],
          'gaoxin7':['chengnanyijia','dongyuan','dayuan','fangcao','gaopeng','guangdu','jinrongcheng','liulichang',
                     'shiyiyiyuan','shenxianshu','tianfuchangcheng','xinhuizhan','xinbei','yuanda','yiguanmiao',
                     'zhongde','zijin','zhonghe'],
          'chenghua':['balixiaoqu','baoligongyuan','chengyulijiao','dongkezhan','dongwuyuan','dongjiaojiyi','jianshelu',
                      'ligongda','longtansi','lijiatuo','mengzhuiwan','smguangchang','simaqiao','wanxiangcheng',
                      'wukuaishi','wannianchang','xinhuagongyuan'],
          'jinniu':['baoligongyuan','chadianzi','dafeng','dongwuyuan','fuqinxiaoqu','gaojiazhaung','guobin','huazhaobi',
                    'huaqiaocheng','huapaifang','jinniuwanda','jinfu','jiulidi','maanlu','shawan','shirenxiaoqu',
                    'shuhanlu','tianhuizhen','tonghuimen','wukuaishi','xipu','xinduchengqu','xinanjiaoda','yingmenkou',
                    'yipintianxia'],
          'tianfuxinqu':['huayang','haiyanggongyuan','jinjiangshengtaidai','luhushengtaicheng','lushan','nanlu','sihe',
                         'yajule'],
          'gaoxinxi1':['gonxinxi','zhonghaiguoji'],
          'shuangliu':['caojinlijiao','dongshengzhen','gongxing','huafu','hangkonggang','jingyuan','jiulonghu',
                       'jiaolonggang','mumashan','nanhu','shuangliuchengqu','wenxingzhen','wanjiawan','xinjian'],
          'wenjiang':['furongguzhen','guanghudadaoyanxian','guosetianxiang','huadudadao','jiaolonggang',
                      'wenjianglaocheng','wenjiangxincheng','zhujiangxincheng'],
          'pidou':['chengwai','huaqiaocheng','hongguang','pixianchengqu','pixianwanda','xipu','xiangshuwan'],
          'longquanyi':['dongshan','damian','honghe','hangtian','longquanyichengqu','qingbaijiang2','shiling2',
                        'yangguangcheng'],
          'xindou':['baoligongyuan','dongwuyuan','dafeng','pihe','qingbaijiang1','shiling1','xipu','xinduchengqu'],
          'tianfuxinqunanqu':['lushan','pengshan','renshou']}
for j in range (1,101):
    for section_name, streetlist in sectionlist.items():
        for street in streetlist:
            houseurl=url.format(areo=street,page=j)
            try:
                res=requests.get(houseurl, verify=False)
                res.encoding='utf-8'
                soup=BeautifulSoup(res.text,'html.parser')
                content=soup.select('.info')
            except Exception as e:
                print(e)
                continue
            #print(content)
            #print (type(content))
            for element in content:
                datum={}
                try:
                    title=element.select('.title')[0].text
                except:
                    title=''
                try:
                    houseinfo=element.select('.houseInfo')[0].text
                except:
                    houseinfo=''
                try:
                    dealDate=element.select('.dealDate')[0].text
                except:
                    houseinfo=''
                try:
                    positionInfo=element.select('.positionInfo')[0].text
                except:
                    positionInfo=''
                try:
                    unitPrice=element.select('.unitPrice')[0].text
                except:
                    unitPrice=''
                try:
                    showprice=element.select('.dealCycleTxt')[0].text
                except:
                    showprice=''
                try:
                    totalPrice=element.select('.totalPrice')[0].text
                except:
                    totalPrice=''
                try:
                    metroline=element.select('.dealHouseTxt')[0].text
                except:
                    metroline=''
                datum['title']=title
                datum['metroline']=metroline
                datum['houseinfo']=houseinfo
                datum['dealDate']=dealDate
                datum['positionInfo']=positionInfo
                datum['unitPrice']=unitPrice
                datum['showprice']=showprice
                datum['totalPrice']=totalPrice
                datum['page']=j
                datum['area']=section_name   #属于哪个区放进去
                datum['mingxi']=street        #区下面的具体街道
                data.append(datum)
                #pprint.pprint(datum)

# 保存成csv    文件
df=pd.DataFrame(data)
# print(data)
df.head()
df.to_csv('./data_out/chengdu.csv')