from bs4 import BeautifulSoup
import re
import requests
import random

#设置请求头
ua=['Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.0; Trident/4.0; FBSMTWB; .NET CLR 2.0.34861; .NET CLR 3.0.3746.3218; .NET CLR 3.5.33652; msn OptimizedIE8;ENUS)',
    'Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20130331 Firefox/21.0',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; fr-ch) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4']
#获取请求返回信息
def GetHtmlText(url):
    try:
        r=requests.get(url,headers={'user-agent':random.choice(ua)})
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return '获取请求返回信息失败'

#格式整理
def my_strip(s):
    #这里的  \ue003  可能会需要修改
    return str(s).replace(" ", "").replace("\n", "").replace("\t", "").replace("\ue003","").strip()

if __name__ == '__main__':
    url='https://beijing.anjuke.com/prop/view/A1513481123?from=filter-saleMetro-salesxq&spread=commsearch_p&position=1&kwtype=filter&now_time=1544251572'
    text = GetHtmlText(url)
    soup = BeautifulSoup(text,'lxml')
    dicts = {}
    for i in range(len(soup.find_all('div',class_="houseInfo-label text-overflow"))):
        x=soup.find_all('div',class_="houseInfo-label text-overflow")[i]
        y=soup.find_all('div',class_="houseInfo-content")[i]
        dicts[x.get_text()]=str(my_strip(y.get_text()))
    print(dicts)