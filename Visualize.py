import pymongo
import requests
import re
import random

#设置请求头
ua=['Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.0; Trident/4.0; FBSMTWB; .NET CLR 2.0.34861; .NET CLR 3.0.3746.3218; .NET CLR 3.5.33652; msn OptimizedIE8;ENUS)',
    'Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20130331 Firefox/21.0',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; fr-ch) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4']
#连接数据库
connection=pymongo.MongoClient()
HouseSource=connection.HouseSource

#获取请求返回信息
def GetHtmlText(url):
    try:
        r=requests.get(url,headers={'user-agent':random.choice(ua)})
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except Exception as e:
        print(e)


#获取小区的经纬度和在卖房屋数量
def GetLatLongAndNum():
    try:
        CommunityNearPOI = HouseSource.CommunityNearPOI
        HouseDetail = HouseSource.HouseDetail
        for item in CommunityNearPOI.find():
            name = item['小区名称']
            url = 'https://restapi.amap.com/v3/place/text?keywords=' + str(name) +'&city=beijing&key='
            msg = GetHtmlText(url)
            #print(msg)
            Community_Num = re.findall('"count":"(.*?)",', msg)[0]
            if Community_Num == '0':
                LatLong = ''
            else:
                LatLong = re.findall(',"location":"(.*?)",',msg)[0]
            print(LatLong)
            CommunityNearPOI.update({"小区名称": name}, {"$set": {'LatLong':LatLong}})
            Num = HouseDetail.find({'所属小区：':name}).count()
            print(Num)
            CommunityNearPOI.update({"小区名称": name}, {"$set": {'Nums': Num}})
        #print(LatLong)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    GetLatLongAndNum()
