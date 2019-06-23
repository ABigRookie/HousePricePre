# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
import requests
import random
import pymongo
import re
import time
import sys
#设置请求头
ua=['Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.0; Trident/4.0; FBSMTWB; .NET CLR 2.0.34861; .NET CLR 3.0.3746.3218; .NET CLR 3.5.33652; msn OptimizedIE8;ENUS)',
    'Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20130331 Firefox/21.0',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; fr-ch) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4']
#分解行政区ID
def GetDistID(fpath):
    try:
        f = open(fpath, 'r')
        content=f.read()
        distname = []
        distname.extend(re.findall('<p class="ol-name">(.*?)</p>', content))
        # print(len(distname))
        # print(distname)
        HousePrices = []
        HousePrices.extend(re.findall('<p class="ol-price">(.*?)</p>', content))
        # print(len(HousePrices))
        # print(HousePrices)
        HouseNum = []
        HouseNum.extend(re.findall('<p class="ol-count">(.*?)</p>', content))
        # print(len(HouseNum))
        # print(HouseNum)
        IDs = []
        IDs.extend(re.findall('data-id="(.*?)"', content))
        # print(len(IDs))
        # print(IDs)
        connection = pymongo.MongoClient()
        HouseSource = connection.HouseSource
        DistBoundary = HouseSource.DistBoundary
        DistBoundary.create_index([("Distname", 1)], unique=True)
        for i in range(len(distname)):
            distdict={}
            distdict['Distname']=distname[i]
            distdict['Price']=HousePrices[i]
            distdict['Num']=HouseNum[i]
            distdict['ID']=IDs[i]
            DistBoundary.insert(distdict)
        f.close()
        return distname
    except:
        return '分解行政区ID出错'
#分解街区ID
def GetBlockID(DistName):
    try:
        fpath = './北京地区信息/'+ str(DistName) + '.txt'
        f = open(fpath,'r')
        content = f.read()
        BlockName=[]
        BlockName.extend(re.findall('<p class="ol-name">(.*?)</p>',content))
        BlockID=[]
        BlockID.extend(re.findall('data-id="(.*?)"',content))
        BlockMidPrice=[]
        BlockMidPrice.extend(re.findall('data-midprice="(.*?)"',content))
        BlockCount=[]
        BlockCount.extend(re.findall('<p class="ol-count">(.*?)</p>',content))
        connection = pymongo.MongoClient()
        HouseSource = connection.HouseSource
        BlockBoundary = HouseSource.BlockBoundary
        # BlockBoundary.create_index("BlockID", unique=True)
        # print(len(BlockName),len(BlockID),len(BlockMidPrice),len(BlockCount))
        # print(BlockName,BlockID,BlockMidPrice,BlockCount)
        for i in range(len(BlockName)):
            # print(i)
            Blocklist={}
            Blocklist['BlockName'] = BlockName[i]
            Blocklist['BlockID'] = BlockID[i]
            Blocklist['BlockMidPrice'] = BlockMidPrice[i]
            Blocklist['BlockCount'] = BlockCount[i]
            Blocklist['DistName'] = str(DistName)
            # print(Blocklist)
            BlockBoundary.insert(Blocklist)
        # print('已完成'+ str(DistName) +'行政区的数据存入')
        f.close()
    except:
        return '分解街区ID出错'
#发送请求获取返回
def GetRequests(url):
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
            'Cookie':'wmda_visited_projects=%3B6289197098934; browse_comm_ids=368953; wmda_new_uuid=1; wmda_session_id_6289197098934=1540468329964-55450fa3-e478-c83c; wmda_uuid=a01133e230747d71970c6a1034f8e426; twe=2; sessid=E0FC0A62-489E-4546-98FD-6D9E1A740E24; ctid=14; new_uv=6; lps=http%3A%2F%2Fwww.anjuke.com%2F%7Chttps%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3D6mbGCmtn9W6vLQndZFqPcwlYBMhgn4Jh36RsF3uhXU01QFkupGBlpvNJ78rNTNu3%26wd%3D%26eqid%3Dd6875895000127f4000000035bd18501; init_refer=https%253A%252F%252Fwww.baidu.com%252Flink%253Furl%253DoTPGRUfvnNX7UaAXVa4afMCpcdkGaR6OkaLxSI07xPRTBmtZoo2ptx9JQG9SByrb%2526wd%253D%2526eqid%253Df1589aed0000b465000000035bd1ae5f; _gat=1; propertys=oasi8j-ph323m_; __xsptplus8=8.6.1540468331.1540468335.3%232%7Cwww.baidu.com%7C%7C%7C%7C%23%231q0ydO36rraWCj1hIP8f3IFxsHj57_YU%23; _gid=GA1.2.1593408605.1540348562; als=0; aQQ_ajkguid=475632FA-3DAC-8B04-96B7-BE003E71A28A; 58tj_uuid=48192f53-0f09-4e54-9bd4-c32467b8ddc1; __xsptplusUT_8=1; _ga=GA1.2.1232027748.1540348562; new_session=0; ajk_member_captcha=b4ba96112e77e1f4c2fa2cc432eabccb',
        }
        r=requests.get(url,headers=headers,timeout=4)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return '获取请求返回出错'
#处理返回获取边界
def GetBoundary(finurl,BlockID,collection,idname):
    try:
        content = GetRequests(finurl)
        # print(content)
        flag=re.findall('"code":(.*?),',content)[0]
        print(flag)
        if flag == None:
            print('需要验证')
            sys.exit()
        else:
            if int(flag) == -1:
                print(BlockID+'该区无边界')
                collection.update({idname:BlockID}, {"$set": {"shape": None}})
                collection.update({idname:BlockID}, {"$set": {"url": None}})
            elif int(flag) == 0:
                area=re.findall(':[[][[](.*?)[]][}][}]',content)[0]
                print(BlockID+':'+area)
                collection.update({idname: BlockID}, {"$set": {"shape": area}})
                collection.update({idname: BlockID}, {"$set": {"url": None}})
    except:
        return '边界信息获取出错'

if __name__ == '__main__':
    fpath ='./北京地区信息/总表.txt'
    '''首先获得行政区ID信息'''
    # GetDistID(fpath)
    '''接下来获取街区ID信息'''
    # connection = pymongo.MongoClient()
    # HouseSource = connection.HouseSource
    # DistBoundary = HouseSource.DistBoundary
    # for item in DistBoundary.find():
    #     print('接下来进行'+item['Distname']+'行政区所含的街区的数据录入')
    #     GetBlockID(item['Distname'])
    '''接下来获取街区请求连接存入数据库'''
    # connection = pymongo.MongoClient()
    # HouseSource = connection.HouseSource
    # BlockBoundary= HouseSource.BlockBoundary
    # url = 'https://beijing.anjuke.com/v3/ajax/map/sale/boundary/?block_id='
    # for item in BlockBoundary.find():
    #     finurl= url + item['BlockID']
    #     BlockBoundary.update({"BlockID": item['BlockID']}, {"$set": {"url": finurl}})
    # BlockBoundary.remove({'url': None})
    '''接下来获取行政区请求连接存入数据库'''
    connection = pymongo.MongoClient()
    HouseSource = connection.HouseSource
    DistBoundary= HouseSource.DistBoundary
    # url = 'https://beijing.anjuke.com/v3/ajax/map/sale/boundary/?region_id='
    # for item in DistBoundary.find():
    #     finurl= url + item['ID']
    #     DistBoundary.update({"ID": item['ID']}, {"$set": {"url": finurl}})
    # DistBoundary.remove({'url': None})
    '''获取街区边界信息'''
    # for item in BlockBoundary.find():
    #     if item['url'] == None:
    #         continue
    #     else:
    #         print('开始获取'+item['BlockID']+'街区边界，链接为:'+item['url'])
    #         GetBoundary(item['url'],item['BlockID'])
    #         time.sleep(3)
    '''获取行政区边界信息'''
    # for item in DistBoundary.find():
    #     if item['url'] == None:
    #         continue
    #     else:
    #         print('开始获取'+item['ID']+'街区边界，链接为:'+item['url'])
    #         GetBoundary(item['url'],item['ID'],DistBoundary,'ID')
    #         time.sleep(3)
    '''处理边界'''
    # for item in DistBoundary.find():
    #     if item['shape'] == None:
    #         continue
    #     else:
    #         print('开始处理'+item['ID']+'街区边界')
    #         # str=item['shape'].replace('"', '')
    #         # str = item['shape'][:-1]
    #         lng=[]
    #         lng=re.findall('[[](.*?),',item['shape'])
    #         lat=[]
    #         lat=re.findall('[0-9],(.*?)[]]',item['shape'])
    #         print(len(lng),len(lat),lng,lat)
    #         for i in range(len(lng)):
    #             if i == 0:
    #                 str = '['+lat[i] + ',' + lng[i] +'],'
    #             else:
    #                 str = str + '['+lat[i] + ',' + lng[i] +'],'
    #         str = str[:-1]
    #         print(str)
    #         DistBoundary.update({"ID": item['ID']}, {"$set": {"shape": str}})






