# -*- coding: utf-8 -*-
import requests
import re
import pymongo
import random
import time
#连接数据库
connection=pymongo.MongoClient()
HouseSource=connection.HouseSource

#POI类型编号
types = ['090100','090601','141204','141203','141202','141201','150500','150700','060400','060100','160100','160300','050100','050200','050300','050500','080101','080111','080601','110101']
TypesKey = ['综合医院','药店','幼儿园','小学','中学','高等院校','地铁站','公交站','超市','商场','银行','ATM','中餐厅','外国餐厅','快餐厅','咖啡厅','体育馆','健身中心','电影院','公园']

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
    except Exception as e:
        print(e)

#提取出所有小区
def CreateCommunityDB():
    try:
        HouseDetail = HouseSource.HouseDetail
        CommunityNearPOI = HouseSource.CommunityNearPOI
        CommunityNearPOI.insert({'小区名称':'北纬40度(东区)'})
        for item in HouseDetail.find():
            CommunityName = item['所属小区：']
            if CommunityNearPOI.find({'小区名称':CommunityName}).count() == 0:
                print(CommunityName)
                CommunityNearPOI.insert({'小区名称':CommunityName})
    except Exception as e:
        print(e)

#首先获取小区的经纬度
def GetLatLong(name):
    try:
        url = 'https://restapi.amap.com/v3/place/text?keywords=' + str(name) +'&city=beijing&key=70cfe8605882530d550644f927ab4257'
        msg = GetHtmlText(url)
        #print(msg)
        Community_Num = re.findall('"count":"(.*?)",', msg)[0]
        if Community_Num == '0':
            LatLong = ''
        else:
            LatLong = re.findall(',"location":"(.*?)",',msg)[0]
        #print(LatLong)
        return LatLong
        #print(LatLong)
    except Exception as e:
        print(e)

#获取小区周边2000米内的POI数据
def GetPOINearby():
    try:
        CommunityNearPOI = HouseSource.CommunityNearPOI
        CommunityNearPOIUrlList = HouseSource.CommunityNearPOIUrlList
        counts = 0
        for item in CommunityNearPOI.find():
            if item['flag'] == str(1):
                counts = int(counts) + 1
                continue
            else:
                name = item['小区名称']
                LatLong = GetLatLong(name)
                #print(LatLong)
                if LatLong == '':
                    counts = int(counts) + 1
                    print('****************第'+str(counts)+'个小区已经获取失败进行跳过*****************')
                    continue
                else:
                    #print(1)
                    #print(LatLong)
                    #更新记录
                    for num in range(len(types)):
                        #print(num)
                        #print(1)
                        #print(CommunityNearPOI.find({'小区名称':name,TypesKey[num]:None}).count())
                        #在这里需要设计断点续传，使得程序在中断后仍能直接从中断点继续，而不用从头开始。
                        if CommunityNearPOI.find({'小区名称':name,TypesKey[num]:None}).count() != 0:
                            url = 'https://restapi.amap.com/v3/place/around?key=70cfe8605882530d550644f927ab4257&location=' + str(LatLong) + '&radius=2000&types=' + str(types[num])
                            #print(url)
                            POI_Msg = GetHtmlText(url)
                            POI_Num = re.findall('"count":"(.*?)",',POI_Msg)[0]
                            print(str(name) + '共有' + str(TypesKey[num]) + POI_Num + '个')
                            CommunityNearPOI.update({"小区名称": name}, {"$set": {str(TypesKey[num]):POI_Num}})
                    counts = int(counts) + 1
                    CommunityNearPOI.update({"小区名称": name}, {"$set": {'flag':'1'}})
                    print('****************第'+str(counts)+'个小区已经获取完毕*****************')
    except Exception as e:
        print(e)

#扫描所有房屋信息将小区周边POI数据导入房屋信息库中
def CombineCommunityPOI():
    try:
        HouseDetail = HouseSource.HouseDetail
        CommunityNearPOI = HouseSource.CommunityNearPOI
        countnum = 0
        for item in HouseDetail.find():
            communityname = item['所属小区：']
            ID = item['_id']
            #print(communityname)
            if CommunityNearPOI.find({'小区名称': communityname,'综合医院':None}).count() != 0:
                print('****************** ID:' + str(ID) + ' 找不到匹配信息********************')
                continue
            else:
                if item['flag'] == '0':
                    print('****************** ID:' + str(ID) + ' 开始整合信息********************')
                    CommunityNearPOI_item = CommunityNearPOI.find_one({'小区名称': communityname})
                    #print(CommunityNearPOI_item)
                    for typesname in TypesKey:
                        POI_num = CommunityNearPOI_item[str(typesname)]
                        HouseDetail.update({'_id':ID},{"$set":{typesname:POI_num}})
                        print('ID:' + str(ID) + ' 周边有' + typesname + POI_num +'个')
                    print('****************** ID:' + str(ID) +' 信息已同步完毕********************')
                    HouseDetail.update({'_id':ID},{"$set":{'flag':'1'}})
                else:
                    continue
    except Exception as e:
        print(e)


if __name__ == '__main__':
    #CreateCommunityDB()
    #GetPOINearby()
    CombineCommunityPOI()