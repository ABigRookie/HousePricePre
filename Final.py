from sklearn.externals import joblib
import random
import re
import requests
import numpy as np
import pandas as pd
import warnings
from sklearn.linear_model import Ridge
from sklearn import preprocessing


types = ['090100','090601','141204','141203','141202','141201','150500','150700','060400','060100','160100','160300','050100','050200','050300','050500','080101','080111','080601','110101']
TypesKey = ['综合医院','药店','幼儿园','小学','中学','高等院校','地铁站','公交站','超市','商场','银行','ATM','中餐厅','外国餐厅','快餐厅','咖啡厅','体育馆','健身中心','电影院','公园']
Types = ['hospital','pharmacy','kindergarten','primary','middle','universities','subwaystation','busstop','supermarket','mall','bank','ATM','chineseres','foreignres','fastres','café','stadium','gym','cinema','park']


ua=['Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.0; Trident/4.0; FBSMTWB; .NET CLR 2.0.34861; .NET CLR 3.0.3746.3218; .NET CLR 3.5.33652; msn OptimizedIE8;ENUS)',
    'Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20130331 Firefox/21.0',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; fr-ch) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4']


def GetHtmlText(url):
    try:
        r=requests.get(url,headers={'user-agent':random.choice(ua)})
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except Exception as e:
        print(e)


def ready_for_predict():
    choose = input('是否开始进行预测?[Y/N]')
    if choose == 'Y' or choose == 'y':
        get_address()
    elif choose == 'N' or choose == 'n':
        print('程序退出')
        exit()
    else:
        print('输入为非法字符,请重新输入！')
        ready_for_predict()


def get_address():
    try:
        print('----------接下来进行必填项的填写----------')
        address = input('请输入预测目标地址(例：朝阳门内大街75号院)')
        if str(address) == 'exit':
            exit()
        else:
            res = GetLatLong(str(address))
            #print(res)
            if res == '0':
                print('该地址无法匹配，请检查地址信息是否输入错误！')
                get_address()
            elif res == '1':
                print('所查询地址并不在北京市，请检查地址信息是否输入错误！\n')
                get_address()
            else:
                get_poi_nearby(res)
                get_house_type()
    except Exception as e:
        print(e)


def GetLatLong(name):
    try:
        url = 'https://restapi.amap.com/v3/place/text?keywords=' + str(
            name) + '&city=beijing&key=********************'
        msg = GetHtmlText(url)
        # print(msg)
        Community_Num = re.findall('"count":"(.*?)",', msg)[0]
        if Community_Num == '0':
            LatLong = '0'
        else:
            pname = re.findall(',"pname":"(.*?)",', msg)[0]
            if pname == '北京市':
                LatLong = re.findall(',"location":"(.*?)",', msg)[0]
                district = re.findall(',"adname":"(.*?)",',msg)[0]
                #print(district)
                district = district.strip('区')
                districts = ['密云','延庆','怀柔','房山','昌平', '顺义', '通州','门头沟','大兴','石景山','丰台','朝阳', '海淀','东城','西城']
                if district not in districts:
                    predice_list['district'] = '北京周边'
                else:
                    predice_list['district'] = district
                #print(predice_list['district'])
            else:
                LatLong = '1'
        # print(LatLong)
        return LatLong
        # print(LatLong)
    except Exception as e:
        print(e)


def get_poi_nearby(LatLong):
    try:
        for num in range(len(types)):
            url = 'https://restapi.amap.com/v3/place/around?key=70cfe8605882530d550644f927ab4257&location=' + str(
                LatLong) + '&radius=2000&types=' + str(types[num])
            POI_Msg = GetHtmlText(url)
            POI_Num = re.findall('"count":"(.*?)",', POI_Msg)[0]
            predice_list[Types[num]] = POI_Num
    except Exception as e:
        print(e)


def get_house_type():
    try:
        all = input('输入顺序为_室_厅_卫(以空格隔开，例：3 1 1)')
        str_sum = 0
        dig_sum = 0
        spa_sum = 0
        other_sum = 0
        for strs in all:

            if strs.isalpha():
                str_sum += 1

            elif strs.isdigit():
                dig_sum += 1

            elif strs == ' ':
                spa_sum += 1

            else:
                other_sum += 1
        if spa_sum == 2 and dig_sum == 3:
            room, living, bath = all.split()
            predice_list['shi'] = room
            predice_list['ting'] = living
            predice_list['wei'] = bath
            get_houseonly()
        else:
            print('输入不满足标准，请重新输入！')
            get_house_type()
    except Exception as e:
        print(e)


def get_houseonly():
    try:
        houseonly = input('请输入是否为唯一住房("是"或"否")')
        if houseonly == 'exit':
            exit()
        else:
            houseonly_type = ['是', '否']
            if houseonly not in houseonly_type:
                print('输入不符合标准，请重新输入！')
                get_houseonly()
            else:
                print('----------接下来进行非必填项的填写----------')
                predice_list['houseonly'] = houseonly
                get_orientation()
    except Exception as e:
        print(e)


def get_orientation():
    try:
        orientation = input('请输入房屋的朝向(请填入以下列出的朝向中的一种：)\n 东，西，南，北，东北，东南，西北，西南，南北，东西')
        if orientation == 'exit':
            exit()
        elif orientation == '':
            predice_list['orientation'] = '南北'
            get_types()
        else:
            orientations = ['东','西','南','北','东北','东南','西北','西南','南北','东西']
            if orientation not in orientations:
                print('输入不符合标准，请重新输入！')
                get_orientation()
            else:
                predice_list['orientation'] = orientation
                get_types()
    except Exception as e:
        print(e)


def get_types():
    try:
        types = input('请输入房屋的类型(请填入以下列出的属性中的一种：)\n 公寓，其它，别墅，四合院，平房，普通住宅')
        if types == 'exit':
            exit()
        elif types == '':
            predice_list['types'] = '普通住宅'
            get_decoration()
        else:
            house_types = ['公寓', '其它', '别墅', '四合院', '平房', '普通住宅']
            if types not in house_types:
                print('输入不符合标准，请重新输入！')
                get_types()
            else:
                predice_list['types'] = types
                get_decoration()
    except Exception as e:
        print(e)


def get_decoration():
    try:
        decoration = input('请输入房屋的装修程度(请填入以下列出的程度中的一种：)\n 简单装修，精装修，毛坯，豪华装修')
        if decoration == 'exit':
            exit()
        elif decoration == '':
            predice_list['decoration'] = '精装修'
            get_yearlimits()
        else:
            decorations = ['简单装修', '精装修', '毛坯', '豪华装修']
            if decoration not in decorations:
                print('输入不符合标准，请重新输入！')
                get_decoration()
            else:
                predice_list['decoration'] = decoration
                get_yearlimits()
    except Exception as e:
        print(e)


def get_yearlimits():
    try:
        yearlimits = input('请输入房屋的房本年限(请填入以下列出的年限中的一种：)\n 满二年，不满二年，满五年')
        if yearlimits == 'exit':
            exit()
        elif yearlimits == '':
            predice_list['yearlimits'] = '满二年'
            get_heating()
        else:
            yearlimits_type = ['满二年', '不满二年', '满五年']
            if yearlimits not in yearlimits_type:
                print('输入不符合标准，请重新输入！')
                get_yearlimits()
            else:
                predice_list['yearlimits'] = yearlimits
                get_heating()
    except Exception as e:
        print(e)


def get_heating():
    try:
        heating = input('请输入房屋的供暖类型(请填入以下列出的类型中的一种：)\n 无，自供暖，集体供暖')
        if heating == 'exit':
            exit()
        elif heating == '':
            predice_list['heating'] = '无'
            feature_processing()
        else:
            heating_type = ['无', '自供暖', '集体供暖']
            if heating not in heating_type:
                print('输入不符合标准，请重新输入！')
                get_heating()
            else:
                predice_list['heating'] = heating
                feature_processing()
    except Exception as e:
        print(e)


def map_values(full):
    try:
        full["odistrict"] = full.district.map({'北京周边': 1,
                                               '密云': 2, '延庆': 2,
                                               '怀柔': 3, '房山': 3,
                                               '昌平': 4, '顺义': 4, '通州': 4,
                                               '门头沟': 4, '大兴': 4,
                                               '石景山': 5,
                                               '丰台': 6,
                                               '朝阳': 7,
                                               '海淀': 8, '东城': 10,
                                               '西城': 12})
        full["oorientation"] = full.orientation.map({'南北': 1,
                                                     '南': 2,
                                                     '东北': 3, '东南': 3, '东西': 3,
                                                     '北': 3, '西': 3, '西北': 3,
                                                     '西南': 3,
                                                     '东': 4,
                                                     })
        full["oyearlimits"] = full.yearlimits.map({'不满二年': 1,
                                                   '满二年': 3,
                                                   '满五年': 2})
        full["otypes"] = full.types.map({'其它': 1,
                                         '别墅': 2, '公寓': 2,
                                         '普通住宅': 3,
                                         '平房': 4,
                                         '四合院': 5})
        full["oheating"] = full.heating.map({'自供暖': 1,
                                             '集体供暖': 2,
                                             '无': 3})
        full["odecoration"] = full.decoration.map({'毛坯': 1,
                                                   '简单装修': 2, '精装修': 2,
                                                   '豪华装修': 2})
        full["ohouseonly"] = full.houseonly.map({'是': 1,
                                                 '否': 2})
        print('--------------非数值型数据处理完毕--------------')
        #print(full.isnull().any())
        #print(full)
        return full
    except Exception as e:
        print(e)


def feature_processing():
    try:
        #print(predice_list)
        df = pd.DataFrame(predice_list, index=[0])
        #print(df)
        print('******************正在处理数据*****************')
        df = map_values(df)
        all_df = df.drop(['orientation', 'types', 'decoration', 'yearlimits', 'heating', 'houseonly', 'district'], axis=1)
        print('----------数据处理完毕，下面开始进行预测----------')
        load_model(all_df)
    except:
        print('')


def load_model(df):
    try:
        filename = 'predict_model.sav'
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            loaded_model = joblib.load(filename)
        res = loaded_model.predict(df)
        res = np.expm1(res)
        print('\n价格预测完毕，预测价格为   ' + str(res[0]) + '  元/平方米')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    print('*****************************************')
    print('\n           北京市房价预测小工具              ')
    print('\n produced by : 范俊超    张祎凡    符 桐\n')
    print('*****************************************')
    predice_list = {}
    ready_for_predict()
    exits = input('\n预测结束，请按任意键退出')
