import numpy as np
import pandas as pd
from pandas import Series,DataFrame

import matplotlib.pyplot as plt
#import seaborn as sns

import csv
import random

#路径
path = 'D:/HouseSource_HouseDetail.csv'
out_test_path = 'D:/HouseSource_HouseDetail_test.csv'
out_train_path ='D:/HouseSource_HouseDetail_train.csv'

#将数据集分为训练集和测试集，比例7:3
def GetTrainData():
    with open(path,'r+',newline='') as file:
        csvreader =  csv.reader(file)
        a = next(csvreader)
        with open(out_test_path, 'w+', newline='') as out_test_file:
            csvwriter_test = csv.writer(out_test_file)
            csvwriter_test.writerow(a)
        with open(out_train_path,'w+',newline='') as  out_train_file:
            csvwriter_train = csv.writer(out_train_file)
            csvwriter_train.writerow(a)
        #print(a)
        for row in csvreader:
            #print(row)
            randoms = random.randint(1,10)
            if randoms <= 2:
                with open(out_test_path, 'a', newline='') as out_test_file:
                    csvwriter_test = csv.writer(out_test_file)
                    csvwriter_test.writerow(row)
            else:
                with open(out_train_path, 'a', newline='') as  out_train_file:
                    csvwriter_train = csv.writer(out_train_file)
                    csvwriter_train.writerow(row)

if __name__ == '__main__':
    GetTrainData()