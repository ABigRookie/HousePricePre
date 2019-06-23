# -*- coding: utf-8 -*-
# 导出数据库所有记录的标准模版
import pymongo
import csv
# 初始化数据库
mongo_url = "127.0.0.1:27017"
DATABASE = input('请输入数据库名:')
TABLE = input('请输入表名:')

client = pymongo.MongoClient(mongo_url)
db_des = client[DATABASE]
db_des_table = db_des[TABLE]


# 将数据写入到CSV文件中

# newline='' 的作用是防止结果数据中出现空行，专属于python3
fpath = 'D://' + DATABASE +'_' + TABLE +'.csv'
with open(fpath, "a", newline='',encoding="utf-8") as csvfileWriter:
    writer = csv.writer(csvfileWriter)
    # 先写列名
    # 写第一行，字段名
    fieldList = input('请输入字段名(以逗号间隔):')
    FieldList = fieldList.split(",")
    writer.writerow(FieldList)

    allRecordRes = db_des_table.find()
    # 写入多行数据
    for record in allRecordRes:
        print(record)
        recordValueLst = []
        for field in FieldList:
            if field not in record:
                recordValueLst.append("None")
            else:
                recordValueLst.append(record[field])
        try:
            writer.writerow(recordValueLst)
        except Exception as e:
            print(f"write csv exception. e = {e}")
