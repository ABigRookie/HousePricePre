# -*- coding: utf-8 -*-

import requests
import re
import time
import pymongo
from bs4 import BeautifulSoup
import random
import sys
#连接数据库
connection=pymongo.MongoClient()
HouseSource=connection.HouseSource
HouseUrl = HouseSource.HouseUrl
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

# 格式整理
def my_strip(s):
    # 这里的  \ue003  可能会需要修改
    return str(s).replace(" ", "").replace("\n", "").replace("\t", "").replace("\ue003", "").strip()

#解析房源信息存入数据库
def GetHouseSourceDetail(url,title):
    try:
        print('*************************开始'+url+'的解析**************************')
        dicts = {}
        text = GetHtmlText(url)
        soup = BeautifulSoup(text, 'lxml')
        if soup.find_all('div', class_="houseInfo-label text-overflow"):
            for i in range(len(soup.find_all('div', class_="houseInfo-label text-overflow"))):
                x = soup.find_all('div', class_="houseInfo-label text-overflow")[i]
                y = soup.find_all('div', class_="houseInfo-content")[i]
                dicts[x.get_text()] = str(my_strip(y.get_text()))
            dicts['title']=str(title)
            print(dicts)
            HouseDetail=HouseSource.HouseDetail
            HouseDetail.insert(dicts)
            HouseUrl.delete_one(item)
        else:
            print("当前网页需要验证，请进行验证:\n" + url)
            sys.exit()
    except:
        return '获取房源信息失败'


#解析页面信息获取房源信息列表存入数据库
def GetHouseSourceList(url):
    try:
        #解析首页网址获取不同地区的前50页房源网页
        text = GetHtmlText(url)
        #print(text)
        soup = BeautifulSoup(text,'lxml')
        #print(soup.text)
        DistUrlList = HouseSource.DistUrlList
        for x in soup.find('span',class_='elems-l').children:
            if(x.name!='span'):
                for i in range(1,51):
                    DistMes={}
                    DistMes['url']=(x['href']+'p'+str(i)+'/')
                    DistMes['DistName']=(x['title'])
                    # print(DistMes['url'],DistMes['DistName'])
                    DistMes['Flag']=(1)
                    DistUrlList.insert(DistMes)

        HouseUrl = HouseSource.HouseUrl
        for item in DistUrlList.find():
            counts = 1
            text = GetHtmlText(item['url'])
            soup = BeautifulSoup(text, 'lxml')
            print("******************开始" + str(item['url'] + '的爬取***********************'))
            for x in soup.find_all('a', class_="houseListTitle"):
                HouseMes = {}
                print(x['href'] + '\n' + x['title'])
                HouseMes['url'] = (x['href'])
                HouseMes['title'] = (x['title'])
                HouseMes['flag'] = (1)
                HouseUrl.insert(HouseMes)
                counts += 1
            if counts == 1:
                print("当前网页需要验证，请进行验证:\n" + str(item['url']))
                sys.exit()
            else:
                DistUrlList.delete_one(item)
                print('**********************' + str(item['url']) + '信息已经爬取完毕，共计有' + str(
                    counts - 1) + '条数据*****************************')
            time.sleep(2)
    except:
        return '房源网页获取失败'

if __name__ == '__main__':
    #安居客首页网址
    # url='https://beijing.anjuke.com/sale/'
    # GetHouseSourceList(url)
    for item in HouseUrl.find():
        GetHouseSourceDetail(item['url'],item['title'])